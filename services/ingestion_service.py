from playwright.sync_api import sync_playwright

from config.settings import HEADLESS, CSV_PATH, MAX_PAGES
from services.ricoh_browser import login_and_go_history, find_history_frame
from services.ricoh_scraper import extract_all_pages
from utils.csv_utils import append_new_jobs, load_latest_created_at

def run_ingestion():

    latest_known_dt = load_latest_created_at(CSV_PATH)
    print(f"Latest stored Created At: {latest_known_dt}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        login_and_go_history(page)
        frame = find_history_frame(page)

        jobs = extract_all_pages(
            frame,
            latest_known_dt=latest_known_dt,
            max_pages=MAX_PAGES,
        )

        context.close()
        browser.close()

    written = append_new_jobs(CSV_PATH, jobs)

    print(f"Total candidate jobs scraped : {len(jobs)}")
    print(f"New appended to CSV          : {written}")
    print(f"CSV path                     : {CSV_PATH}")