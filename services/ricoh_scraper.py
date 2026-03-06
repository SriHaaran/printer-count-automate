import re
from datetime import datetime
from models.print_job import PrintJob

def parse_datetime(s):
    s = " ".join(s.split())
    for fmt in ("%m/%d/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except:
            continue
    return None

def scrape_page(frame):
    rows = frame.locator("tr:has(td.listData)")
    jobs = []

    for i in range(rows.count()):
        tds = rows.nth(i).locator("td.listData")
        if tds.count() < 6:
            continue

        job_id = tds.nth(0).inner_text().strip()
        if not re.fullmatch(r"\d+", job_id):
            continue

        user_id = tds.nth(2).inner_text().strip()
        if user_id in ("---", ""):
            user_id = "UNKNOWN"

        file_name = tds.nth(3).inner_text().strip()

        nobrs = tds.nth(5).locator("nobr")
        created = f"{nobrs.nth(0).inner_text().strip()} {nobrs.nth(1).inner_text().strip()}"

        jobs.append(PrintJob(job_id, user_id, file_name, created))

    return jobs