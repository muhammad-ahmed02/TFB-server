# Database
# https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': 'mydatabase',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'd292op9ngu1r3m',
        'USER': 'dyopwxyfvvshru',
        'PASSWORD': '4fdfdf5b8a38e3827d9f0bb794cb1d415a0c015685f16fee534c19dfa87f24b6',
        'HOST': 'ec2-44-196-174-238.compute-1.amazonaws.com',
        'PORT': '5432',
    }
}
