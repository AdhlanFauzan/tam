#coding: utf-8
from fatturazione.views.money_util import moneyfmt, NumberedCanvas
from reportlab.lib.pagesizes import A4, portrait, landscape #@UnusedImport
from django import http
from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate
from reportlab.lib.units import cm
from django.conf import settings
from reportlab.platypus import Frame, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import copy
import os
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
import datetime
from reportlab.platypus.flowables import Spacer, KeepTogether
from tam.models import Listino, Luogo

test = settings.DEBUG
test = False

styles = getSampleStyleSheet()
normalStyle = copy.deepcopy(styles['Normal'])
normalStyle.fontSize = 8
normalStyle.fontName = 'Helvetica'

logoImage_path = os.path.join(settings.MEDIA_ROOT, settings.OWNER_LOGO)

LISTINO_FOOTER = getattr(settings, 'LISTINO_FOOTER', None)

normal_style = ParagraphStyle(name='Normal')
normal_right_style = ParagraphStyle(name='NormalRight', alignment=TA_RIGHT)
table_right = ParagraphStyle(name='TableBold', alignment=TA_RIGHT, fontSize=8)
table_normal = ParagraphStyle(name='TableNormal', alignment=TA_LEFT, fontSize=8)
table_normal_right = ParagraphStyle(name='TableNormalLeft', alignment=TA_RIGHT, fontSize=8)


def onPageListino(canvas, doc):
	width, height = canvas._doctemplate.pagesize
	canvas.saveState()
	anno = datetime.date.today().year
	setPdfProperties(canvas, 'Listino %d' % anno)

	# in alto a sinistra
	y1 = height - doc.topMargin
	x = doc.leftMargin

	logo_height = 2.5 * cm
	y1 -= logo_height
	if not test: canvas.drawImage(logoImage_path, x=x, y=y1, width=7 * cm, height=logo_height)

	# in alto a destra
	y2 = height - doc.topMargin
	x = width - 8 * cm - doc.rightMargin

	consorzio = Paragraph('<font size="8"><b>%s</b></font>' % settings.DATI_CONSORZIO.strip().replace('\n', '<br/>'), normal_right_style)
	consorzio.wrapOn(canvas, 8 * cm, y2)
	consorzio.drawOn(canvas, x=x, y=y2 - consorzio.height)
	y2 -= consorzio.height + 10

	descrittore = Paragraph('<font size="14"><b>Listino %s</b></font>' % doc.listino.nome, normal_right_style)
	descrittore.wrapOn(canvas, 8 * cm, y2)
	descrittore.drawOn(canvas, x=x, y=y2 - descrittore.height)
	y2 -= descrittore.height + 10

	x = doc.leftMargin

	# footer
	footer_style = ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontSize=8)

	footer_height = 0
	if LISTINO_FOOTER:
		note_finali_lines = [LISTINO_FOOTER]
		note_finali = Paragraph("<br/>".join(note_finali_lines),
							footer_style)
		note_finali.wrap(width - doc.rightMargin - doc.leftMargin, 5 * cm)
		note_finali.drawOn(canvas, doc.leftMargin, doc.bottomMargin)
		footer_height = note_finali.height
	y = min(y1, y2)

	doc.pageTemplate.frames = [
			Frame(doc.leftMargin, doc.bottomMargin + footer_height,
				   width - (doc.leftMargin + doc.rightMargin), y - doc.bottomMargin - footer_height,
				   showBoundary=test), #x,y, width, height
		]
	canvas.restoreState()


def setPdfProperties(canvas, title):
	# set PDF properties ***************
	canvas.setFont('Helvetica', 8)
	canvas.setAuthor(settings.LICENSE_OWNER)
	canvas.setCreator('TaM v.%s' % settings.TAM_VERSION)
	canvas._doc.info.producer = ('TaM')
	canvas.setSubject(u"%s" % title)
	canvas.setTitle(title)


def getTabellaListino(doc, righe_prezzo, tipo_servizio, luogoDiRiferimento):
	width, height = portrait(A4)
	tabellaListino = []
	prezzi = sorted(
					righe_prezzo,
					key=lambda p: (p.tipo_servizio, p.tratta.da.nome.lower(), p.tratta.a.nome.lower(), p.max_pax)
					)

	for prezzo in prezzi:
		if prezzo.tipo_servizio <> tipo_servizio: continue # skip collettivi
		da, a = prezzo.tratta.da, prezzo.tratta.a
		if da == luogoDiRiferimento:
			tratta = a
		else:
			tratta = "%s - %s" % (da, a)

		if a.nome[0] == '.':	# tratta in evidenza
			tratta = "<b>%s</b>" % tratta

		tabellaListino.append([
							tratta,
							prezzo.prezzo_diurno,
							prezzo.prezzo_notturno,
							prezzo.max_pax, 	# aggiungo i pax
							])

	# -------- Creo la nuova Tabella Listino con i pax se necessari ------------------
	nuovaTabellaListino = [('Destinazione', 'Importo', Paragraph('<b><font size="10">Notturno</font><br/>(dalle 22 alle 6)</b>', table_right))]
	precedente = None
	sottoTratte = 0
	for riga in tabellaListino:	# ripasso il listino, aggiungo il numero di pax se necessario
		nome_tratta, diurno, notturno, pax = riga
		if nome_tratta == precedente:
			if sottoTratte == 0: # prima sottotratta, divido
				print "raggruppo", nome_tratta
				primaRiga = nuovaTabellaListino[-1]
				# creo una nuova riga uguale alla prima, ma senza prezzi
				nuovaTabellaListino.append([
						Paragraph("%s pax" % primaRiga[3], table_right), # metto i pax
						primaRiga[1],
						primaRiga[2],
						primaRiga[3]
					]
				)
				# e tolgo i prezzi dalla prima
				primaRiga[1] = primaRiga[2] = primaRiga[3] = ""
				tratta_da_scrivere = pax

			tratta_da_scrivere = Paragraph("%s pax" % pax, table_right)
			sottoTratte += 1
		else:
			sottoTratte = 0
			tratta_da_scrivere = Paragraph("%s" % nome_tratta, table_normal) if nome_tratta else "",
		precedente = nome_tratta
		nuovaTabellaListino.append([
					tratta_da_scrivere,
					Paragraph("€ %s" % moneyfmt(diurno), table_normal_right),
					Paragraph("€ %s" % moneyfmt(notturno), table_normal_right),
					pax
				]
			)

	taxiStyle = TableStyle([
						('VALIGN', (0, 0), (-1, -1), 'TOP'),
						('ALIGN', (0, 0), (-1, -1), 'RIGHT'), 	# globalmente allineato a destra...
						('ALIGN', (0, 0), (1, -1), 'LEFT'), 	# tranne la prima colonna (con la descrizione)
						('GRID', (0, 1), (-1, -1), 0.1, colors.grey),
						('FACE', (0, 0), (-1, -1), 'Helvetica'),

						('FACE', (0, 0), (-1, 0), 'Helvetica-Bold'), 	# header
						('SIZE', (0, 0), (-1, -1), 10),

				])
	colWidths = ((width - doc.leftMargin - doc.rightMargin) - (3 * cm) * 2,) + (3 * cm,) * 2
	if len(nuovaTabellaListino) > 1:
		return Table(
							[riga[:3] for riga in nuovaTabellaListino],
							style=taxiStyle,
							colWidths=colWidths,
							repeatRows=1
						) #, style=righeStyle, repeatRows=1, colWidths=colWidths)


def export(listino, luogoDiRiferimento):
	response = http.HttpResponse(mimetype='application/pdf')
	width, height = portrait(A4)

	pageTemplates = [
					 PageTemplate(id='Listino', onPage=onPageListino),
					]

	doc = BaseDocTemplate(
						response,
						pagesize=(width, height),
						leftMargin=1 * cm,
						rightMargin=1 * cm,
						bottomMargin=1.5 * cm,
						topMargin=1 * cm,
						showBoundary=test,
						pageTemplates=pageTemplates,
					)

	doc.listino = listino	# arricchisco il doc

	righe_prezzo = listino.prezzolistino_set.all()

	story = []

	listinoEsclusivo = getTabellaListino(doc, righe_prezzo, 'T', luogoDiRiferimento)
	if listinoEsclusivo:
		title = Paragraph("SERVIZIO TAXI ESCLUSIVO", normalStyle)
		story.append(title)
		story.append(listinoEsclusivo)

	listinoCollettivo = getTabellaListino(doc, righe_prezzo, 'C', luogoDiRiferimento)
	if listinoEsclusivo and listinoCollettivo:
		story.append(Spacer(1, 1.5 * cm))
	if listinoCollettivo:
		title = Paragraph("SEVIZIO COLLETIVO MINIBUS", normalStyle)
		story.append(KeepTogether( [title, listinoCollettivo]))

	if not listinoCollettivo and not listinoEsclusivo:
		story.append("Non abbiamo nessuna corsa specificata nel listino.")


	doc.build(story, canvasmaker=NumberedCanvas)
	return response

if __name__ == "__main__":
	export(Listino.objects.get(id=181), Luogo.objects.get(id=55))
