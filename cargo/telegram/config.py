import os
from dotenv import load_dotenv

load_dotenv()


TELEGRAM_API_URL = os.environ.get("TELEGRAM_API_URL")
TELEGRAM_API_KEY = os.environ.get("TELEGRAM_API_KEY")
