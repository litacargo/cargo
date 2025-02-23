import os
from dotenv import load_dotenv

load_dotenv()


TELEGRAM_API_URL = os.environ.get("TELEGRAM_API_URL")
TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")

TRANSIT_API_URL = f"{TELEGRAM_API_URL}/api/v1/notification/transit"
CHINA_API_URL = f"{TELEGRAM_API_URL}/api/v1/notification/china"
BISHKEK_API_URL = f"{TELEGRAM_API_URL}/api/v1/notification/bishkek"