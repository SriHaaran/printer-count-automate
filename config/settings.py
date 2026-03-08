import os
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_env(name: str) -> str:
    """
    Helper function to fetch required environment variables.
    Raises error if missing.
    """
    value = os.getenv(name)

    if value is None or value.strip() == "":
        raise RuntimeError(f"Environment variable '{name}' is not set in .env")

    return value

# Timezone used for scheduler and timestamps
TZ = ZoneInfo(get_env("TZ"))

# Printer Web Image Monitor URL
PRINTER_BASE_URL = get_env("PRINTER_BASE_URL")

# Printer login credentials
LOGIN_USER = get_env("LOGIN_USER")
LOGIN_PASS = os.getenv("LOGIN_PASS", "")  # password can be blank

# Whether Playwright runs browser in headless mode
HEADLESS = get_env("HEADLESS").lower() == "true"

# Interval between scraping runs (seconds)
POLL_SECONDS = int(get_env("POLL_SECONDS"))

# Location of CSV storage file for scraped print history
CSV_PATH = get_env("CSV_PATH")

# MS Access database location
ACCESS_DB_PATH = get_env("ACCESS_DB_PATH")

# Maximum pagination safety limit
MAX_PAGES = int(get_env("MAX_PAGES"))