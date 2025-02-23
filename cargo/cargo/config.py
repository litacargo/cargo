import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get("POSTGRESQL_HOST")
DB_PORT = os.environ.get("POSTGRESQL_PORT")
DB_NAME = os.environ.get("POSTGRESQL_DBNAME")
DB_USER = os.environ.get("POSTGRESQL_USER")
DB_PASS = os.environ.get("POSTGRESQL_PASSWORD")

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = os.environ.get("CSRF_TRUSTED_ORIGINS")

SECRET_KEY_ENV = os.environ.get("SECRET_KEY")
CELERY_BROKER_URL_ENV =  os.environ.get("CELERY_BROKER_URL")
DEBUG_BOOL =  os.environ.get("DEBUG_BOOL")

SITE_NAME = os.environ.get("SITE_NAME")