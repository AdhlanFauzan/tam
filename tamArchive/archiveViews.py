#coding: utf-8
import datetime
import time
from decimal import Decimal
from django import forms
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
import logging
from django.db import transaction
#from django.db import connection
from django.db.models import Q
from tam.models import Viaggio, ProfiloUtente, Conducente, \
	get_classifiche
from tamArchive.models import ViaggioArchive
from tam.views.tamviews import SmartPager

from django.utils.datastructures import SortedDict # there are Python 2.4 OrderedDict, I use django to relax requirements
from django.contrib import messages
from modellog.models import ActionLog
from modellog.actions import logAction, stopLog, startLog
from tam import tamdates

archiveNotBefore_days = 180

def menu(request, template_name="archive/menu.html"):
	dontHilightFirst = True
	if not request.user.has_perm('tamArchive.archive') and not request.user.has_perm('tamArchive.flat'):
		messages.error(request, "Devi avere accesso o all'archiviazione o all'appianamento.")
		return HttpResponseRedirect(reverse("tamUtil"))

	class ArchiveForm(forms.Form):
		""" Form che chiede una data non successiva a 30 giorni fa """
		end_date_suggested = (tamdates.ita_today() - datetime.timedelta(days=archiveNotBefore_days)).replace(month=1, day=1).strftime('%d/%m/%Y')
		end_date = forms.DateField(
								   label="Data finale",
								   input_formats=[_('%d/%m/%Y')],
								   initial=end_date_suggested
								   )

	form = ArchiveForm()

	return render_to_response(template_name,
			{
				"dontHilightFirst": dontHilightFirst,
				"form": form,
				"mediabundleJS": ('tamUI',),
				"mediabundleCSS": ('tamUI',),
			}
			, context_instance=RequestContext(request))


@transaction.commit_manually(using="archive")
def action(request, template_name="archive/action.html"):
	""" Archivia le corse, mantenendo le classifiche inalterate """
	if not request.user.has_perm('tamArchive.archive'):
		messages.error(request, "Devi avere accesso all'archiviazione.")
		return HttpResponseRedirect(reverse("tamArchiveUtil"))

	end_date_string = request.POST.get("end_date")
	try:
		timetuple = time.strptime(end_date_string, '%d/%m/%Y')
		end_date = datetime.date(timetuple.tm_year, timetuple.tm_mon, timetuple.tm_mday)
	except:
		end_date = None
	if (end_date is None):
		messages.error(request, "Devi specificare una data valida per archiviare.")
		return HttpResponseRedirect(reverse("tamArchiveUtil"))
	max_date = tamdates.ita_today() - datetime.timedelta(days=archiveNotBefore_days)
	if end_date > max_date:
		messages.error(request, "La data che hai scelto è troppo recente. Deve essere al massimo il %s." % max_date)
		return HttpResponseRedirect(reverse("tamArchiveUtil"))

	# non archivio le non confermate

	archiveTotalCount = Viaggio.objects.count()
	archiveCount = Viaggio.objects.filter(data__lt=end_date, conducente__isnull=False).count()

	logDaEliminare = ActionLog.objects.filter(data__lt=end_date)
	logTotalCount = ActionLog.objects.count()
	logCount = logDaEliminare.count()
	archive_needed = archiveCount or logCount

	if "archive" in request.POST:
		from tamArchive.tasks import do_archiviazioneTask
		do_archiviazioneTask(request.user, end_date) #@UndefinedVariable
		messages.info(request, "Archiviazione iniziata.")

		return HttpResponseRedirect(reverse("tamArchiveUtil"))

	return render_to_response(template_name,
							 {"archiveCount":archiveCount, "archiveTotalCount":archiveTotalCount,
							  "logCount":logCount, "logTotalCount":logTotalCount,
							  "archive_needed":archive_needed,
							  "end_date":end_date,
							  "end_date_string":end_date_string,
							},
							context_instance=RequestContext(request))


def view(request, template_name="archive/view.html"):
	""" Visualizza le corse archiviate """
	profile = ProfiloUtente.objects.get(user=request.user)
	from django.core.paginator import Paginator
	archiviati = ViaggioArchive.objects.filter(padre__isnull=True)
	paginator = Paginator(archiviati, 100, orphans=10)	# pagine da tot righe (cui si aggiungono i figli)

	try: page = int(request.GET.get("page"))
	except: page = 1
	paginator.smart_page_range = SmartPager(page, paginator.num_pages).results

	try:
		thisPage = paginator.page(page)
		list = thisPage.object_list
	except:
		messages.warning(request, "Pagina %d vuota." % page)
		thisPage = None
		list = []

	luogoRiferimento = profile.luogo.nome

	return render_to_response(
		template_name,
		{'list':list, 'paginator':paginator, 'luogoRiferimento':luogoRiferimento, 'thisPage':thisPage },
		context_instance=RequestContext(request)
		)

def flat(request, template_name="archive/flat.html"):
	""" Livella le classifiche, in modo che gli ultimi abbiano zero """
	if not request.user.has_perm('tamArchive.flat'):
		messages.error(request, "Devi avere accesso all'appianamento.")
		return HttpResponseRedirect(reverse("tamArchiveUtil"))

	classificheViaggi = get_classifiche()

	def trovaMinimi(c1, c2):
		""" Date due classifiche (2 conducenti) ritorna il minimo """
		keys = ("puntiDiurni", "puntiNotturni",
				"prezzoDoppioPadova", "prezzoVenezia", "prezzoPadova")
		results = SortedDict()
		for key in keys:
			v1, v2 = c1[key], c2[key]
			if type(v1) is float: v1 = Decimal("%.2f" % v1)	# converto i float in Decimal
			if type(v2) is float: v2 = Decimal("%.2f" % v2)
			results[key] = min(v1, v2)
		return results

	minimi = reduce(trovaMinimi, classificheViaggi)
	flat_needed = (max(minimi.values()) > 0)	# controllo che ci sia qualche minimo da togliere
	if "flat" in request.POST and flat_needed:
		logAction("F",
					instance=request.user,
					description="Appianamento delle classifiche",
					user=request.user)
		logging.debug("FLAT delle classifiche")
		stopLog(Conducente)
		for conducente in Conducente.objects.all():
			conducente.classifica_iniziale_diurni -= minimi["puntiDiurni"]
			conducente.classifica_iniziale_notturni -= minimi["puntiNotturni"]
			conducente.classifica_iniziale_doppiPadova -= minimi['prezzoDoppioPadova']
			conducente.classifica_iniziale_long -= minimi['prezzoVenezia']
			conducente.classifica_iniziale_medium -= minimi['prezzoPadova']
			conducente.save()

		startLog(Conducente)
		messages.success(request, "Appianamento effettuato.")
		return HttpResponseRedirect(reverse("tamArchiveUtil"))

	return render_to_response(template_name, {"minimi":minimi, 'flat_needed':flat_needed},
							 context_instance=RequestContext(request))
