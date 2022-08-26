# Database
# https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#databases

import os


local = False

if local:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'mydatabase',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.environ.get('DB_NAME', 'd292op9ngu1r3m'),
            'USER': os.environ.get('DB_USER_NAME', 'dyopwxyfvvshru'),
            'PASSWORD': os.environ.get('DB_PASSWORD', '4fdfdf5b8a38e3827d9f0bb794cb1d415a0c015685f16fee534c19dfa87f24b6'),
            'HOST': os.environ.get('DB_HOST', 'ec2-44-196-174-238.compute-1.amazonaws.com'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
