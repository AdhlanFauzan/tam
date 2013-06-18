# coding: utf-8
import os
import logging
from socket import gethostname
host = gethostname().lower()

TAM_VERSION = "5.6"
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

if host in ("dariosky", "acido", "dario"):
	DEBUG = True  # siamo in Test
else:
	DEBUG = False

# DEBUG = False
TEMPLATE_DEBUG = DEBUG

if DEBUG:
	# set naive Datetime as errors
	import warnings
	warnings.filterwarnings(
			'error', r"DateTimeField received a naive datetime",
			RuntimeWarning, r'django\.db\.models\.fields')
	#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

ADMINS = (
	('Dario Varotto', 'dario.varotto@gmail.com'),
)

MANAGERS = ADMINS
DATABASES = {}  # set them in settings_local

DATABASE_ROUTERS = ['db_routers.TamArchiveRouter',
					'modellog.db_routers.SeparateLogRouter']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be avilable on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Rome'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'it-it'
USE_L10N = True
# USE_THOUSAND_SEPARATOR = True # mi incasina gli invii delle form

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True  # mi serve per le date

# Absolute path to the directory that holds media.
MEDIA_ROOT = os.path.join(PROJECT_PATH, "media/")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
STATIC_ROOT = os.path.join(PROJECT_PATH, 'static/')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
	# Put strings here, like "/home/html/static" or "C:/www/django/static".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
# 	'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


# List of callables that know how to import templates from various sources.
if not DEBUG:
	TEMPLATE_LOADERS = (
		('django.template.loaders.cached.Loader', 	(# cache template loaders
			'django.template.loaders.filesystem.Loader',
			'django.template.loaders.app_directories.Loader',
			)
		),
	)


MIDDLEWARE_CLASSES = (
	'mediagenerator.middleware.MediaMiddleware',
# 	'django.middleware.gzip.GZipMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	# 'django.middleware.csrf.CsrfViewMiddleware', # check requests for csrf
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'tam.middleware.loginRequirement.RequireLoginMiddleware',
# 	'django.middleware.doc.XViewMiddleware',	# currently useless?

	'django.middleware.transaction.TransactionMiddleware',

	'tam.middleware.threadlocals.ThreadLocals',
	# 'tam.middleware.sqlLogMiddleware.SQLLogMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates"
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
)


TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	'django.core.context_processors.request',
	"django.contrib.messages.context_processors.messages",
	'django.core.context_processors.static',

	"license.context_processors.license_details",
	)


LICENSE_OWNER = ''  # to be shown on the footer
DATI_CONSORZIO = """"""  # to be printed on the invoices
OWNER_LOGO = 'fatture/logo.jpg'  # relative to media folder
INVOICES_FOOTERS = {}  # a dictionary with <invoinces type>:<list of footers>

# MEDIA GENERATOR **********
MEDIA_DEV_MODE = DEBUG
DEV_MEDIA_URL = '/mediadev/'
PRODUCTION_MEDIA_URL = '/mediaprod/'
GLOBAL_MEDIA_DIRS = (os.path.join(os.path.dirname(__file__), 'media'),)
MEDIA_BUNDLES = (
	# CSS *************
	('tam.css', 'css/tam.css',),
	('prenotazioni.css', 'css/prenotazioni.css',),
	('tam-stealth.css', 'css/tam-stealth.css',),
	('fatturaHtml.css', 'css/fatture.css',),
	('tamUI.css',
		'js/jquery-ui-1.9.1.custom/css/ui-lightness/jquery-ui-1.9.1.custom.min.css',
		'css/tam.css',
	),
	# JS **************
	('tambase.js',
		'js/jquery.min.js', 'js/jquery.hotkeys.js',
		'js/tam-common.js',
	),
	('tamUI.js',
		'js/jquery.min.js', 'js/jquery.hotkeys.js',
		'js/jquery-ui-1.9.1.custom/js/jquery-ui-1.9.1.custom.min.js', 'js/calendarPreferences.js',
		'js/tam-common.js',
	),
	('tamCorse.js',
		'js/jquery.min.js', 'js/jquery.hotkeys.js',
		'js/jquery-ui-1.9.1.custom/js/jquery-ui-1.9.1.custom.min.js', 'js/calendarPreferences.js',
		'js/tam-common.js', 'js/jquery.scrollTo-min.js', 'js/listaCorse.js',
	),
	('selFatture.js', 'js/fatture/table_selector.js'),
	('tamRules.css', 'css/tamrules.css'),
	('jquery.editable-1.3.3.js', 'js/jquery.editable-1.3.3.js'),
	('fattura.js', 'js/fatture/fattura.js'),

)
YUICOMPRESSOR_PATH = os.path.join(PROJECT_PATH, 'yuicompressor.jar')
if os.path.exists(YUICOMPRESSOR_PATH):
	ROOT_MEDIA_FILTERS = {
		'js': 'mediagenerator.filters.yuicompressor.YUICompressor',
		'css': 'mediagenerator.filters.yuicompressor.YUICompressor',
	}
# **************************

INSTALLED_APPS = [
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
# 	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',

	'django.contrib.admin',
	'django.contrib.admindocs',
	'django.contrib.humanize',
	'mediagenerator',

	'tam',
	'south',
	'tamArchive',

	'fatturazione',

	'modellog',

# 	'license',

	'djangotasks',  # let's use djangotasks instead of celery
]

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'xxx@xxx.com'
# EMAIL_HOST_PASSWORD = 'xxx'
# EMAIL_PORT = 587
EMAIL_SUBJECT_PREFIX = "[TaM]"

if DEBUG:
	SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 14 giorni in debug
else:
	SESSION_COOKIE_AGE = 30 * 60  # cookie age in seconds (30 minutes)

# import datetime
# LICENSE_EXPIRATION = datetime.date(2010, 01, 01)

#===============================================================================
# Set to True to use the debug_toolbar
use_debug_toolbar = DEBUG and False
if use_debug_toolbar:
	# put the debug toolbar middleware right after the Gzip middleware
	try:
		# middleware_split_position = MIDDLEWARE_CLASSES.index('django.middleware.gzip.GZipMiddleware') + 1
		middleware_split_position = 0  #  put the toolbar middleware at the start
		MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES[:middleware_split_position] + \
						('debug_toolbar.middleware.DebugToolbarMiddleware',) + \
						MIDDLEWARE_CLASSES
	except:
		pass
# 	MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ('debug_toolbar.middleware.DebugToolbarMiddleware',)
	DEBUG_TOOLBAR_CONFIG = {"INTERCEPT_REDIRECTS":False}
	INTERNAL_IPS = ('127.0.0.1',)
	INSTALLED_APPS = INSTALLED_APPS + ('debug_toolbar',)
#===============================================================================

# PASSWORD_HASHERS = (
# 	'django.contrib.auth.hashers.SHA1PasswordHasher',  # Still use the old hashing until I pass to 1.4
# 	'django.contrib.auth.hashers.PBKDF2PasswordHasher',
# 	'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
# 	'django.contrib.auth.hashers.BCryptPasswordHasher',
# 	'django.contrib.auth.hashers.MD5PasswordHasher',
# 	'django.contrib.auth.hashers.CryptPasswordHasher',
# )

TAM_VIAGGI_PAGINA = 100

# ******************* CACHE
CACHES = {
	'default': {
		'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
		'LOCATION': 'TaM',
	}
# 	'default': {
# 		'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
# 		'LOCATION': '127.0.0.1:11211',
# 	}
}

# Usiamo le sessioni su cookies per evitare di importunare il DB
# ha lo svantaggio che non sappiamo quali sessioni sono attive, per poter identificare quelle scadute
# SESSION_ENGINE = "django.contrib.sessions.backends.signed_cookies"

NOMI_DEFINIZIONE_FATTURE = [ "FattureConsorzio", "FattureNoIVA",
							 "FattureConducente", "FattureConducenteNoIva",
							 "Ricevute"]

try:
	from settings_local import *  # @UnusedWildImport
except ImportError:
	logging.warning("'settings_local.py' has not been found. Use this to keep out of VC secret settings.")
	pass

SECURE_STORE_LOCATION = os.path.join(PROJECT_PATH, 'media_secured')
SECURE_URL = "/secure/"

for app, desc in PLUGGABLE_APPS.items():
	INSTALLED_APPS.append(app)

# from celeryconfig import * #@UnusedWildImport
# import djcelery
# djcelery.setup_loader()
