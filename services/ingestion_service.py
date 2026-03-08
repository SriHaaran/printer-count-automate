from playwright.sync_api import sync_playwright

from config.settings import HEADLESS, CSV_PATH, MAX_PAGES, ACCESS_DB_PATH
from services.ricoh_browser import login_and_go_history, find_history_frame
from services.ricoh_scraper import extract_all_pages

from utils.csv_utils import append_new_jobs, load_latest_created_at
from utils.access_utils import insert_new_jobs_to_access

def run_ingestion():
    """
    Execute one scraping cycle:
    1. read latest stored Created At from CSV
    2. scrape printer history
    3. append new rows to CSV
    4. append same new rows to Access
    """
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
    
    csv_written = append_new_jobs(CSV_PATH, jobs)
    access_written = insert_new_jobs_to_access(ACCESS_DB_PATH, jobs)

    print(f"Total candidate jobs scraped : {len(jobs)}")
    print(f"New appended to CSV          : {csv_written}")
    print(f"New inserted to Access       : {access_written}")