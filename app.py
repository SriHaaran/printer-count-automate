import os
from datetime import datetime, time, timedelta
from playwright.sync_api import sync_playwright
import csv
import sys

from config.settings import TZ, OUTPUT_ROOT, STATE_DIR, HEADLESS
from utils.state_utils import get_state_path, load_state, save_state
from utils.excel_utils import append_jobs_by_user
from services.ricoh_browser import login_and_go_history, find_history_frame
from services.ricoh_scraper import scrape_page

def get_excel_path(day_str: str) -> str:
    return os.path.join(OUTPUT_ROOT, day_str, f"PrinterJobHistory_{day_str}.xlsx")

def run_job(window_start: datetime, window_end: datetime, use_state: bool = True):
    day_str = window_end.astimezone(TZ).strftime("%Y-%m-%d")
    excel_path = get_excel_path(day_str)

    seen = set()
    state_path = get_state_path(STATE_DIR, day_str)

    if use_state:
        state = load_state(state_path)
        seen = set(state.get("seen_job_ids", []))
    else:
        state = {"seen_job_ids": []}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        login_and_go_history(page)
        frame = find_history_frame(page)

        jobs = scrape_page(frame)
        # jobs = extract_jobs_in_window(frame, window_start, window_end)
        print("\n===== RAW JOB DATA (CSV) =====\n")

    writer = csv.writer(sys.stdout)
    writer.writerow(["JobID", "UserID", "FileName", "CreatedAt"])

    for job in jobs:
       writer.writerow([
            job.job_id,
            job.user_id,
            job.file_name,
            job.created_at
    ])

    print("\n===== END DATA =====\n")

    print(f"Total rows scraped: {len(jobs)}")

    return

    #     context.close()
    #     browser.close()

    # filtered = []
    # for job in jobs:
    #     if (not use_state) or (job.job_id not in seen):
    #         filtered.append(job)
    #         seen.add(job.job_id)

    # written = append_jobs_by_user(excel_path, filtered)

    # if use_state:
    #     state["seen_job_ids"] = list(seen)[-10000:]
    #     save_state(state_path, state)

    # print(f"Window start : {window_start}")
    # print(f"Window end   : {window_end}")
    # print(f"Jobs found   : {len(jobs)}")
    # print(f"Jobs written : {written}")
    # print(f"Excel path   : {excel_path}")

    # return {
    #     "jobs_found": len(jobs),
    #     "jobs_written": written,
    #     "excel_path": excel_path,
    # }

def run_today_full_day():
    now_local = datetime.now(TZ)
    today_local = now_local.date() 
    # start date - 30 days
    start_date = today_local - timedelta(days=30)

    start_dt = datetime.combine(start_date, time(0, 0, 0), tzinfo=TZ)
    end_dt = datetime.combine(today_local, time(23, 59, 59), tzinfo=TZ)

    return run_job(start_dt, end_dt, use_state=False)

if __name__ == "__main__":
    run_today_full_day()