import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = "147.45.247.199"
DB_PORT = 5432
DB_NAME = "gen_user"
DB_USER = "django"
DB_PASS = "UYvg3\3\o;Pz\:"

ALLOWED_HOSTS = "litacargo-cargo-4ad0.twc1.net"
CSRF_TRUSTED_ORIGINS = "https://litacargo-cargo-4ad0.twc1.net"

SECRET_KEY_ENV = "django-insecure-u!8*-id8w+j(j5#x2zhx9t@yxr1y_yknnp1!nvqnf@zw)_^1)b"
CELERY_BROKER_URL_ENV = "redis://default:O%xk|JC0Bo@Ifl@192.168.0.4:6379"
DEBUG_BOOL = False

SITE_NAME = "Lita"