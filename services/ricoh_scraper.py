import re
from datetime import datetime
from models.print_job import PrintJob
from config.settings import TZ


def parse_datetime(s):
    s = " ".join(s.split())
    for fmt in ("%m/%d/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
        try:
            naive_dt = datetime.strptime(s, fmt)
            return naive_dt.replace(tzinfo=TZ)
        except ValueError:
            continue
    return None

def scrape_page(frame):
    """
    Debug-first scraper:
    - locates table.reportListCommon
    - iterates all tr
    - treats rows with >= 7 td.listData cells as data rows
    """
    tables = frame.locator("table.reportListCommon")
    table_count = tables.count()
    print(f"reportListCommon tables found: {table_count}")

    if table_count == 0:
        print("No reportListCommon table found in frame.")
        return []

    table = tables.first
    row_locator = table.locator("tr")
    row_count = row_locator.count()
    print(f"Total <tr> in report table: {row_count}")

    jobs = []

    for i in range(row_count):
        tr = row_locator.nth(i)
        tds = tr.locator("td.listData")
        td_count = tds.count()

        if td_count == 0:
            continue

        print(f"Row {i}: td.listData count = {td_count}")

        # Data rows should contain 7 columns:
        # ID, User Name, User ID, File Name, Status, Created At, Page(s)
        if td_count < 7:
            continue

        try:
            job_id = tds.nth(0).inner_text().strip()
            user_id = tds.nth(2).inner_text().strip()
            file_name = tds.nth(3).inner_text().strip()

            created_td = tds.nth(5)
            nobrs = created_td.locator("nobr")
            if nobrs.count() >= 2:
                created_at = f"{nobrs.nth(0).inner_text().strip()} {nobrs.nth(1).inner_text().strip()}"
            else:
                created_at = created_td.inner_text().strip()

            print(
                f"Parsed row {i}: "
                f"job_id={job_id!r}, user_id={user_id!r}, file_name={file_name!r}, created_at={created_at!r}"
            )

            if not re.fullmatch(r"\d+", job_id):
                print(f"Skipping row {i}: invalid job_id")
                continue

            if user_id in ("---", ""):
                user_id = "UNKNOWN"

            jobs.append(PrintJob(job_id, user_id, file_name, created_at))

        except Exception as e:
            print(f"Error parsing row {i}: {e}")

    return jobs