import os
from zoneinfo import ZoneInfo

TZ = ZoneInfo(os.getenv("TZ", "Asia/Kuala_Lumpur"))

PRINTER_BASE_URL = os.getenv("PRINTER_BASE_URL", "http://192.168.1.44")
LOGIN_USER = os.getenv("LOGIN_USER", "admin")
LOGIN_PASS = os.getenv("LOGIN_PASS", "")

OUTPUT_ROOT = os.getenv("OUTPUT_ROOT", "/data/output")
STATE_DIR = os.getenv("STATE_DIR", "/data/state")

HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

WORK_START = os.getenv("WORK_START", "08:00")
WORK_END = os.getenv("WORK_END", "17:00")

POLL_WORK_SECONDS = int(os.getenv("POLL_WORK_SECONDS", "300"))
POLL_AFTER_SECONDS = int(os.getenv("POLL_AFTER_SECONDS", "200"))

WORK_WINDOW_BUFFER_SECONDS = int(os.getenv("WORK_WINDOW_BUFFER_SECONDS", "120"))
AFTER_WINDOW_BUFFER_SECONDS = int(os.getenv("AFTER_WINDOW_BUFFER_SECONDS", "300"))