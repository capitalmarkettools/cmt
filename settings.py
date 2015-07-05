# Django settings for cmt project.
import os

ROOT_PATH = os.path.realpath(os.path.dirname(__file__))

#XXX - make sure in production this is set to False
DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
	#Specify email address where admin information is being sent to including errors and login info
    ('CMT Admin', 'XXX'),
)

#Specify your own site
SITE_ID = 'www.capitalmarkettools.org/cmt'

MANAGERS = ADMINS
DEFAULT_DB_ALIAS=1
DATABASES = {
        'default':{
                   'ENGINE':'django.db.backends.mysql',
					#Enter db name
                   'NAME':'XXX',
					#Enter sa login
                   'USER':'XXX',
					#Enter sa pw
                   'PASSWORD':'XXX',
                   'HOST':'',
                   'PORT':''
        }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(ROOT_PATH, 'static')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
#ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '$crifyv6fx6!0g2(b(75du6x!+k7*njd%vy9i&c7by@%f_yf^6'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader'
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',     
)

ROOT_URLCONF = 'cmt.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(ROOT_PATH, 'templates'),
    os.path.join(ROOT_PATH, 'templates/HistoricalVAR'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'ajax_select',
#    'cmt',
#    'django.contrib.staticfiles',
    'src',
    'contact_form',
    'registration',
    'crispy_forms',
    'report_builder',
)

#SESSION_ENGINE = 'django.contrib.sessions.backends.file'

AUTH_PROFILE_MODULE = 'src.UserProfile'

#Required for ajax-selects
AJAX_LOOKUP_CHANNELS = {
        'hvarconfig': ('src.lookups', 'HvarConfigLookup'),
        'portfolio': ('src.lookups', 'PortfolioLookup'),
        'equity': ('src.lookups', 'EquityLookup'),
        'basis': ('src.lookups', 'BasisLookup'),
        'timePeriod': ('src.lookups', 'TimePeriodLookup')
}

#magically include jqueryUI/js/css
AJAX_SELECT_BOOTSTRAP = True
AJAX_SELECT_INLINES = 'inline'

ACCOUNT_ACTIVATION_DAYS = 7

FIXTURE_DIRS = (os.path.join(ROOT_PATH, 'src\\fixtures'))

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
#Django Email - not sure what it is used for
EMAIL_HOST_USER = 'XXX'
#Django Email passeord - not sure what it is used for
EMAIL_HOST_PASSWORD = 'XXX'
EMAIL_PORT = 587

TEMPLATE_CONTEXT_PROCESSORS=(
                             "django.contrib.auth.context_processors.auth",
                             "django.core.context_processors.debug",
                             "django.core.context_processors.i18n",
                             "django.core.context_processors.media",
                             "django.core.context_processors.static",
                             "django.core.context_processors.tz",
                             "django.contrib.messages.context_processors.messages",
                             "src.contextProcessor.systemDate",
                             "src.contextProcessor.marketId",
                             )

CRISPY_TEMPLATE_PACK = 'uni_form'

#All file locations
BATCH_LOGS = os.path.join(ROOT_PATH, 'logs/')

STATIC_URL = '/static/'

LOGIN_URL = '/cmt/accounts/login/'
LOGOUT_URL = '/cmt/accounts/login/'
LOGIN_REDIRECT_URL = '/cmt/accounts/profile'

