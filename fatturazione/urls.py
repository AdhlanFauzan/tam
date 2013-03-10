'''
Created on 11/set/2011

@author: Dario Varotto
'''
from django.conf.urls import url, patterns

urlpatterns = patterns ('fatturazione.views',
    url(r'^$', 'lista_fatture_generabili', name="tamGenerazioneFatture"),

	url(r'^archivio/$', 'view_fatture', name="tamVisualizzazioneFatture"),

	url(r'archivio/(?P<id_fattura>\d*)/$', 'fattura', name='tamFatturaId'),

	url(r'archivio/export/(?P<id_fattura>\d*)/(?P<export_type>pdf|html)/$',
		'exportfattura',
		name='tamExportFattura'),

	url(r'archivio/export/group/(?P<tipo>.*?)/(?P<export_type>pdf|html)/$',
		'exportmultifattura',
		name='tamExportMultiFattura'),

)

from fatturazione.views.generazione import DEFINIZIONE_FATTURE #@UnresolvedImport
for fatturazione in DEFINIZIONE_FATTURE:
	if not fatturazione.generabile: continue
	urlpatterns += patterns ('fatturazione.views',
		url(fatturazione.url_generazione,
			'genera_fatture',
			{ "fatturazione":fatturazione },
			name=fatturazione.urlname_generazione()
		),
		url(fatturazione.url_generazione.replace("$", "manuale/$"),
			'nuova_fattura', {"fatturazione":fatturazione},
			name=fatturazione.urlname_manuale()
		),
	)
