import sys

# Database
# https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': '{{ project_name }}',
#         'USER': '{{ project_name }}',
#         'PASSWORD': '{{ secret_key|slugify }}',
#         'HOST': 'db',
#         'CONN_MAX_AGE': 900
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase',
    }
}
