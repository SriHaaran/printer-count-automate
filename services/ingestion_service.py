from playwright.sync_api import sync_playwright

from config.settings import HEADLESS, CSV_PATH, ACCESS_DB_PATH, MAX_PAGES
from services.ricoh_browser import login_and_go_history, find_history_frame
from services.ricoh_scraper import extract_all_pages
from utils.csv_utils import append_new_jobs
from utils.access_utils import insert_new_jobs_to_access


def run_ingestion():
    """
    Execute one scraping cycle:
    1. scrape all pages from printer history
    2. append new rows to CSV
    3. insert new rows to MS Access
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        login_and_go_history(page)
        frame = find_history_frame(page)

        jobs = extract_all_pages(frame, max_pages=MAX_PAGES)

        context.close()
        browser.close()

    csv_written = append_new_jobs(CSV_PATH, jobs)
    access_written = insert_new_jobs_to_access(ACCESS_DB_PATH, jobs)

    print(f"Total candidate jobs scraped : {len(jobs)}")
    print(f"New appended to CSV          : {csv_written}")
    print(f"New inserted to Access       : {access_written}")