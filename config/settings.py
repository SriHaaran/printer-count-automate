"""
Global configuration settings for the Ricoh scraping engine.

This module loads environment variables and provides
central configuration values such as:

- printer URL
- login credentials
- scraping interval
- CSV storage location

These values can be overridden using a `.env` file.
"""

import os
from zoneinfo import ZoneInfo

# Timezone used for scheduler and timestamps
TZ = ZoneInfo(os.getenv("TZ", "Asia/Kuala_Lumpur"))

# Printer Web Image Monitor URL
PRINTER_BASE_URL = os.getenv("PRINTER_BASE_URL", "http://192.168.1.44")

# Printer login credentials
LOGIN_USER = os.getenv("LOGIN_USER", "admin")
LOGIN_PASS = os.getenv("LOGIN_PASS", "")

# Whether Playwright runs browser in headless mode
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

# Interval between scraping runs (seconds)
POLL_SECONDS = int(os.getenv("POLL_SECONDS", "300"))

# Location of CSV storage file for scraped print history
CSV_PATH = os.getenv("CSV_PATH", "Y:\\ricoh_print_history\\print_jobs.csv")
ACCESS_DB_PATH = os.getenv("ACCESS_DB_PATH", "Y:\\STAFF WORKING FOLDER\\STAFF\\Mr. Sri\\Backend\\Lemurian_db V7.accdb")

# Location of CSV storage file for scraped print history
MAX_PAGES = int(os.getenv("MAX_PAGES", "100"))