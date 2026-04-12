import re
from typing import List, Dict

from models.print_job import PrintJob
from datetime import datetime
from config.settings import TZ

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

            # Skip processing records that cannot be accessed
            if "processing" in status.lower():
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

def extract_all_pages(frame, max_pages: int = 100):
    """
    Scrape all available history pages from page 1 onward.

    Important:
    We do NOT stop based on Created At timestamp because
    Ricoh history ordering is not strictly sequential by time.

    Stop conditions:
    - no rows found
    - page signature repeats
    - no next page exists
    - max_pages reached
    """
    all_jobs = []
    session_fingerprints = set()
    seen_page_signatures = set()

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

        page_added = 0

        for job in page_jobs:
            fp = build_row_fingerprint(job)

            # avoid duplicate rows within the same scraping session
            if fp in session_fingerprints:
                continue

            session_fingerprints.add(fp)
            all_jobs.append(job)
            page_added += 1

        print(f"Candidate jobs collected from page {page_no}: {page_added}")

        if not goto_next_page(frame):
            break

    print(f"\nTotal candidate jobs scraped across all pages: {len(all_jobs)}")
    return all_jobs

# Additional functions to reach 'Counter per User' page and scrape data from it.
def find_counter_table_context(page):
    """
    Find the frame/page that contains the Counter per User table.
    """
    for frame in page.frames:
        try:
            body = frame.locator("body")
            if body.count() > 0:
                text = body.inner_text(timeout=2000)
                if "Counter per User" in text and "Display Count" in text and "Total Prints" in text:
                    return frame
        except Exception:
            continue

    try:
        body = page.locator("body")
        if body.count() > 0:
            text = body.inner_text(timeout=2000)
            if "Counter per User" in text and "Display Count" in text and "Total Prints" in text:
                return page
    except Exception:
        pass

    raise RuntimeError("Counter per User page/frame not found.")


def set_counter_display_20(ctx):
    """
    Set Display Count dropdown to 20.
    """
    candidates = [
        'select',
        'select[name*="count"]',
        'select[name*="display"]',
    ]

    for sel in candidates:
        try:
            loc = ctx.locator(sel)
            if loc.count() == 0:
                continue

            first = loc.first
            if not first.is_visible():
                continue

            options = first.locator("option")
            for i in range(options.count()):
                txt = options.nth(i).inner_text().strip()
                if txt == "20":
                    first.select_option(label="20")
                    ctx.wait_for_timeout(2500)
                    return
        except Exception:
            continue

    raise RuntimeError("Display Count dropdown with value 20 not found.")


def find_counter_data_table(ctx):
    """
    Find the main counter table containing User / Name / Total Prints / Printer.
    """
    tables = ctx.locator("table")

    for i in range(tables.count()):
        table = tables.nth(i)
        try:
            txt = table.inner_text(timeout=2000)
            if "User" in txt and "Name" in txt and "Total Prints" in txt and "Printer" in txt:
                return table
        except Exception:
            continue

    raise RuntimeError("Counter per User data table not found.")


def scrape_counter_per_user(ctx) -> list[Dict]:
    """
    Scrape one Counter per User page only.
    No pagination required.

    Required fields:
    - PrinterID              -> User
    - TotalPrintsBW          -> Total Prints B&W
    - TotalPrintsColor       -> Total Prints Color
    - TotalPrints            -> B&W + Color
    - PrinterBW              -> Printer Black & White
    - TotalPrintUpdateTime   -> current datetime
    """
    table = find_counter_data_table(ctx)
    rows = table.locator("tr")

    results: list[Dict] = []
    now = datetime.now(TZ)

    for i in range(rows.count()):
        row = rows.nth(i)
        cells = row.locator("td")

        # Header rows / grouping rows won't have enough td columns
        if cells.count() < 11:
            continue

        try:
            printer_id = cells.nth(0).inner_text().strip()
            employee_name = cells.nth(1).inner_text().strip()

            # Based on your screenshot mapping
            total_bw = int((cells.nth(2).inner_text() or "0").replace(",", "").strip())
            total_color = int((cells.nth(3).inner_text() or "0").replace(",", "").strip())
            printer_bw = int((cells.nth(10).inner_text() or "0").replace(",", "").strip())
        except Exception:
            continue

        if not printer_id or not printer_id.isdigit():
            continue

        results.append({
            "PrinterID": printer_id,
            "EmployeeName": employee_name,
            "TotalPrintsBW": total_bw,
            "TotalPrintsColor": total_color,
            "TotalPrints": total_bw + total_color,
            "PrinterBW": printer_bw,
            "TotalPrintUpdateTime": now,
        })

    print(f"Counter rows parsed: {len(results)}")
    return results