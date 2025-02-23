from django.conf import settings
from .config import TELEGRAM_API_KEY

HEADERS = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "X-API-Key": getattr(settings, "API_KEY", TELEGRAM_API_KEY)
}