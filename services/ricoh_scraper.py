import re
from typing import List, Optional

from models.print_job import PrintJob
from datetime import datetime

from utils.csv_utils import parse_created_at, build_row_fingerprint

def scrape_page(frame) -> List[PrintJob]:
    tables = frame.locator("table.reportListCommon")
    if tables.count() == 0:
        print("No reportListCommon table found in frame.")
        return []

    table = tables.first
    rows = table.locator("tr")

    jobs: List[PrintJob] = []

    for i in range(rows.count()):
        tr = rows.nth(i)
        tds = tr.locator("td.listData")
        if tds.count() < 7:
            continue

        try:
            job_id = tds.nth(0).inner_text().strip()

            # Skip non-numeric IDs
            if not re.fullmatch(r"\d+", job_id):
                continue

            user_name = tds.nth(1).inner_text().strip()
            user_id = tds.nth(2).inner_text().strip()
            file_name = tds.nth(3).inner_text().strip()

            # Extract status of the job
            status = tds.nth(4).inner_text().strip()
            
            # Skip restricted records that cannot be accessed
            if "access restricted" in status.lower():
                continue

            created_at = tds.nth(5).inner_text().strip().replace("\n", " ")
            pages = tds.nth(6).inner_text().strip()

            if user_id in ("---", ""):
                user_id = "UNKNOWN"

            jobs.append(PrintJob(
                job_id=job_id,
                user_name=user_name,
                user_id=user_id,
                file_name=file_name,
                status=status,
                created_at=" ".join(created_at.split()),
                pages=pages,
            ))
        except Exception as e:
            print(f"Error parsing row {i}: {e}")

    print(f"Rows parsed from current page: {len(jobs)}")
    return jobs

def get_page_signature(frame) -> str:
    jobs = scrape_page(frame)
    if not jobs:
        return "EMPTY"
    return f"{jobs[0].job_id}-{jobs[-1].job_id}-{len(jobs)}"

def get_page_indicator_text(frame) -> str:

    # Reads pager text like 1/6, 2/6, etc.
    candidates = frame.locator("text=/\\d+\\/\\d+/")
    try:
        count = candidates.count()
        for i in range(count):
            txt = candidates.nth(i).inner_text().strip()
            if re.fullmatch(r"\d+/\d+", txt):
                return txt
    except Exception:
        pass
    return ""

def goto_next_page(frame) -> bool:
    """
    Move only to the next history page.
    Avoid unrelated links like 'Go to [Printer: Print Jobs] >>'.
    """
    before_sig = get_page_signature(frame)
    before_page = get_page_indicator_text(frame)

    print(f"Before page indicator: {before_page}")
    print(f"Before signature     : {before_sig}")

    candidates = []

    try:
        links = frame.locator("a")
        for i in range(links.count()):
            item = links.nth(i)
            if not item.is_visible():
                continue

            text = (item.inner_text() or "").strip()
            href = (item.get_attribute("href") or "").strip()
            title = (item.get_attribute("title") or "").strip()

            blob = " ".join([text, href, title]).lower()

            if "printer: print jobs" in blob:
                continue
            if "refresh" in blob:
                continue
            if "back" in blob:
                continue

            candidates.append((item, blob))
    except Exception:
        pass

    try:
        img_inputs = frame.locator("input[type='image']")
        for i in range(img_inputs.count()):
            item = img_inputs.nth(i)
            if not item.is_visible():
                continue

            alt = (item.get_attribute("alt") or "").strip()
            title = (item.get_attribute("title") or "").strip()
            src = (item.get_attribute("src") or "").strip()

            blob = " ".join([alt, title, src]).lower()
            candidates.append((item, blob))
    except Exception:
        pass

    next_keywords = ["next", "right", ">", "nextr", "nextpage"]

    for item, blob in candidates:
        if not any(k in blob for k in next_keywords):
            continue

        try:
            print(f"Trying next candidate: {blob}")
            item.click(timeout=5000)
            frame.page.wait_for_timeout(2500)

            after_sig = get_page_signature(frame)
            after_page = get_page_indicator_text(frame)

            print(f"After page indicator : {after_page}")
            print(f"After signature      : {after_sig}")

            if after_sig != before_sig and after_sig != "EMPTY":
                print("Pagination success.")
                return True

            # fallback: page indicator changed
            if after_page and before_page and after_page != before_page:
                print("Pagination success by page indicator.")
                return True

        except Exception as e:
            print(f"Next candidate failed: {blob} -> {e}")

    print("No next page found or page did not change.")
    return False

def extract_all_pages(frame, latest_known_dt: Optional[datetime] = None, max_pages: int = 100) -> List[PrintJob]:

    all_jobs: List[PrintJob] = []
    seen_page_signatures = set()
    session_fingerprints = set()

    for page_no in range(1, max_pages + 1):
        print(f"\n=== Scraping page {page_no} ===")

        current_sig = get_page_signature(frame)
        if current_sig in seen_page_signatures:
            print("Page signature already seen. Stopping to avoid loop.")
            break
        seen_page_signatures.add(current_sig)

        page_jobs = scrape_page(frame)
        if not page_jobs:
            print("No jobs found on this page. Stopping.")
            break

        page_new_count = 0
        oldest_dt_on_page: Optional[datetime] = None
        newest_dt_on_page: Optional[datetime] = None

        for job in page_jobs:
            dt = parse_created_at(job.created_at)
            if dt is not None:
                if oldest_dt_on_page is None or dt < oldest_dt_on_page:
                    oldest_dt_on_page = dt
                if newest_dt_on_page is None or dt > newest_dt_on_page:
                    newest_dt_on_page = dt

            fp = build_row_fingerprint(job)

            # avoid duplicates within same scraping run
            if fp in session_fingerprints:
                continue

            session_fingerprints.add(fp)

            # collect everything for now; final dedupe happens before CSV append
            all_jobs.append(job)
            page_new_count += 1

        print(f"Candidate jobs collected from page {page_no}: {page_new_count}")
        print(f"Newest datetime on page {page_no}: {newest_dt_on_page}")
        print(f"Oldest datetime on page {page_no}: {oldest_dt_on_page}")

        # Early stop rule:
        # if the oldest row on this page is already older than or equal to the
        # latest stored timestamp, later pages will also be older.
        if latest_known_dt is not None and oldest_dt_on_page is not None:
            if oldest_dt_on_page <= latest_known_dt:
                print("Oldest row on current page is older than/equal to latest stored timestamp. Stopping pagination early.")
                break

        if not goto_next_page(frame):
            break

    print(f"\nTotal candidate jobs scraped across all pages: {len(all_jobs)}")
    return all_jobs