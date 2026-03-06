import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from config.settings import *
from utils.time_utils import parse_hhmm, compute_window
from utils.state_utils import get_state_path, load_state, save_state
from utils.excel_utils import append_jobs_by_user
from services.ricoh_browser import login_and_go_history, find_history_frame
from services.ricoh_scraper import scrape_page, parse_datetime

def main():
    work_start = parse_hhmm(WORK_START)
    work_end = parse_hhmm(WORK_END)

    while True:
        now = datetime.now(TZ)
        day_str = now.strftime("%Y-%m-%d")

        excel_path = os.path.join(OUTPUT_ROOT, day_str, f"PrinterJobHistory_{day_str}.xlsx")
        state_path = get_state_path(STATE_DIR, day_str)
        state = load_state(state_path)
        seen = set(state["seen_job_ids"])

        window_start, window_end, window_secs = compute_window(
            now, work_start, work_end,
            POLL_WORK_SECONDS, POLL_AFTER_SECONDS,
            WORK_WINDOW_BUFFER_SECONDS, AFTER_WINDOW_BUFFER_SECONDS
        )

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=HEADLESS)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            login_and_go_history(page)
            frame = find_history_frame(page)

            jobs = scrape_page(frame)

            filtered = []
            for job in jobs:
                dt = parse_datetime(job.created_at)
                if dt and window_start <= dt <= window_end:
                    if job.job_id not in seen:
                        filtered.append(job)
                        seen.add(job.job_id)

            append_jobs_by_user(excel_path, filtered)

            state["seen_job_ids"] = list(seen)[-10000:]
            save_state(state_path, state)

            browser.close()

        time.sleep(POLL_WORK_SECONDS if work_start <= now.time() <= work_end else POLL_AFTER_SECONDS)

if __name__ == "__main__":
    main()