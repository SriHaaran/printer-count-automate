import time
from datetime import datetime, timedelta

from config.settings import AFTER_WINDOW_BUFFER_SECONDS, POLL_AFTER_SECONDS, POLL_WORK_SECONDS, TZ, WORK_END, WORK_START, WORK_WINDOW_BUFFER_SECONDS
from utils.time_utils import parse_hhmm, is_working_time
from app import run_job


def compute_window(now: datetime):
    work_start = parse_hhmm(WORK_START)
    work_end = parse_hhmm(WORK_END)

    if is_working_time(now, work_start, work_end):
        seconds = POLL_WORK_SECONDS + WORK_WINDOW_BUFFER_SECONDS
        sleep_seconds = POLL_WORK_SECONDS
    else:
        seconds = POLL_AFTER_SECONDS + AFTER_WINDOW_BUFFER_SECONDS
        sleep_seconds = POLL_AFTER_SECONDS

    window_end = now
    window_start = now - timedelta(seconds=seconds)
    return window_start, window_end, sleep_seconds


def main():
    print("Scheduler started...")

    while True:
        # Now - 1 day
        now = datetime.now(TZ)
        now = now - timedelta(days=1)
        window_start, window_end, sleep_seconds = compute_window(now)

        try:
            run_job(window_start, window_end, use_state=True)
        except Exception as e:
            print(f"Scheduler error: {e}")

        print(f"Sleeping for {sleep_seconds} seconds...\n")
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    main()