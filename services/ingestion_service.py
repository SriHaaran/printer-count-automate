from playwright.sync_api import sync_playwright

from config.settings import HEADLESS, CSV_PATH, ACCESS_DB_PATH, MAX_PAGES
from services.ricoh_browser import login_and_go_history, find_history_frame, goto_counter_per_user_from_home
from services.ricoh_scraper import extract_all_pages, find_counter_table_context, set_counter_display_20, scrape_counter_per_user
from utils.csv_utils import append_new_jobs
from utils.access_utils import insert_new_jobs_to_access, update_employee_print_totals


def run_ingestion():
    """
    Execute one scraping cycle:
    1. scrape all pages from printer history
    2. append new rows to CSV
    3. insert new rows to MS Access
    4. go Home
    5. navigate to Counter per User
    6. scrape total counters
    7. update EmployeeT
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        # Step 1: Printer Job History
        login_and_go_history(page)
        history_frame = find_history_frame(page)
        jobs = extract_all_pages(history_frame, max_pages=MAX_PAGES)

        # Step 2: Counter per User
        goto_counter_per_user_from_home(page)
        counter_ctx = find_counter_table_context(page)
        set_counter_display_20(counter_ctx)
        counter_rows = scrape_counter_per_user(counter_ctx)

        context.close()
        browser.close()

    csv_written = append_new_jobs(CSV_PATH, jobs)
    access_written = insert_new_jobs_to_access(ACCESS_DB_PATH, jobs)
    employee_updated = update_employee_print_totals(ACCESS_DB_PATH, counter_rows)

    print(f"Total candidate jobs scraped : {len(jobs)}")
    print(f"New appended to CSV          : {csv_written}")
    print(f"New inserted to Access       : {access_written}")
    print(f"Total counter rows scraped   : {len(counter_rows)}")
    print(f"EmployeeT rows updated       : {employee_updated}")