'''
Created on 11/set/2011

@author: Dario Varotto
'''
from django.conf.urls.defaults import * #@UnusedWildImport
from fatturazione.views.generazione import filtro_consorzio, filtro_ricevute, \
	filtro_conducente
from fatturazione.models import RigaFattura

urlpatterns = patterns ('fatturazione.views',
    url(r'^$', 'lista_fatture', name="tamGenerazioneFatture"),

    url(r'^genera/consorzio/$', 'genera_fatture', { 'filtro':filtro_consorzio,
													"tipo":"1",
													"template_name":"2-1.fatturazione_consorzio.djhtml",
												},
	   		 name="tamFattureGeneraConsorzio"),

    url(r'^genera/conducente/$', 'genera_fatture', {'filtro':filtro_conducente, "tipo":"2",
												  "keys":["conducente"],
												  "template_name":"2-2.fatturazione_conducente.djhtml",
												  "manager":RigaFattura.objects,
												  "order_by":["conducente", "viaggio__cliente", "fattura__data"],
												  },
	   		 name="tamFattureGeneraConducente"),

	url(r'^genera/ricevute/$', 'genera_fatture', {'filtro':filtro_ricevute, "tipo":"3",
												  "keys":["conducente", "cliente"],
												  "template_name":"2-3.fatturazione_ricevute.djhtml"},
	   		name="tamFattureGeneraRicevute"),

	url(r'^archivio/$', 'lista_fatture', name="tamVisualizzazioneFatture"),
)
