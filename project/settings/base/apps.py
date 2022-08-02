INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',

    'django_extensions',
    'clear_cache',
    'mathfilters',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'corsheaders',
    'rest_framework',
    'rest_framework.authtoken',

    'rest_auth',
    "rest_auth.registration",

    'project.apps.inventory',
)
