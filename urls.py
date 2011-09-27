from django.conf.urls.defaults import * #@UnusedWildImport
from django.conf import settings
import os

#urlpatterns = patterns('',
#	url(r'^$', "django.views.generic.simple.direct_to_template", {'template':'main.html'}, name="main" ),
#)

urlpatterns = patterns ( '',
	( r'', include( 'tam.urls' ) ),
	( r'^archive/', include( 'tamArchive.urls' ) ),
	( r'', include( 'license.urls' ) ),
	( r'^fatture/', include( 'fatturazione.urls' ) ),
 )

from django.contrib import admin
admin.autodiscover()

# Serve media settings to simulate production, we know in REAL production this won't happend
urlpatterns += patterns('',
	("^"+settings.PRODUCTION_MEDIA_URL[1:]+r'(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), '_generated_media')}),
	("^media/"+r'(?P<path>.*)$', 'django.views.static.serve', {'document_root': os.path.join(os.path.dirname(__file__), "media")} ),
	url(r'^admin/', include(admin.site.urls)),
)