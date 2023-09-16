# Database
# https://docs.djangoproject.com/en/{{ docs_version }}/ref/settings/#databases

import os
import dj_database_url

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
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
    # DATABASES = {
    #     'default': {
    #         'ENGINE': 'django.db.backends.postgresql_psycopg2',
    #         'NAME': os.environ.get('DB_NAME', 'd79htkqnf866c2'),
    #         'USER': os.environ.get('DB_USER_NAME', 'zngfvgpojnrsti'),
    #         'PASSWORD': os.environ.get('DB_PASSWORD', '201bd84ecfbf9cb934c6a17be1dd530fbd8526532e3777c5fb4da324d7a7571a'),
    #         'HOST': os.environ.get('DB_HOST', 'ec2-34-236-103-63.compute-1.amazonaws.com'),
    #         'PORT': os.environ.get('DB_PORT', '5432'),
    #     }
    # }
