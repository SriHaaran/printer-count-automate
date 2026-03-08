import csv
import os
from datetime import datetime
from typing import List, Set, Optional

from models.print_job import PrintJob

CSV_HEADERS = ["ID", "User Name", "User ID", "File Name", "Status", "Created At", "Page(s)"]

def ensure_csv_exists(csv_path: str) -> None:
    """
    Ensure CSV file exists. Create it with header if missing.
    """
    folder = os.path.dirname(csv_path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    if not os.path.exists(csv_path):
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

def parse_created_at(dt_str: str) -> Optional[datetime]:
    """
    Parse Ricoh Created At string into datetime.
    Example: 3/7/2026 14:25:18
    """
    cleaned = " ".join((dt_str or "").split())
    for fmt in ("%m/%d/%Y %H:%M:%S", "%d/%m/%Y %H:%M:%S"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None

def build_row_fingerprint(job: PrintJob) -> str:
    """
    Build a stable row fingerprint for deduplication.

    Do NOT rely on printer job ID because Ricoh IDs may reset daily
    or after printer restart.
    """
    return "||".join([
        (job.created_at or "").strip(),
        (job.user_name or "").strip(),
        (job.user_id or "").strip(),
        (job.file_name or "").strip(),
        (job.status or "").strip(),
        (job.pages or "").strip(),
    ])

def load_existing_fingerprints(csv_path: str) -> Set[str]:
    # Load all stored row fingerprints from CSV.
    ensure_csv_exists(csv_path)
    seen: Set[str] = set()

    with open(csv_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            fingerprint = "||".join([
                (row.get("Created At") or "").strip(),
                (row.get("User Name") or "").strip(),
                (row.get("User ID") or "").strip(),
                (row.get("File Name") or "").strip(),
                (row.get("Status") or "").strip(),
                (row.get("Page(s)") or "").strip(),
            ])
            if fingerprint.strip("|"):
                seen.add(fingerprint)

    return seen

def load_latest_created_at(csv_path: str) -> Optional[datetime]:
    """
    Find the latest Created At value already stored in CSV.
    This is used as the pagination stop checkpoint.
    """
    ensure_csv_exists(csv_path)
    latest_dt: Optional[datetime] = None

    with open(csv_path, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dt = parse_created_at(row.get("Created At", ""))
            if dt is None:
                continue
            if latest_dt is None or dt > latest_dt:
                latest_dt = dt

    return latest_dt

def append_new_jobs(csv_path: str, jobs: List[PrintJob]) -> int:
    """
    Append only rows not already present in CSV,
    based on row fingerprint.
    """
    ensure_csv_exists(csv_path)
    existing_fingerprints = load_existing_fingerprints(csv_path)

    new_jobs = []
    for job in jobs:
        fp = build_row_fingerprint(job)
        if fp not in existing_fingerprints:
            new_jobs.append(job)
            existing_fingerprints.add(fp)

    if not new_jobs:
        return 0

    with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        for job in new_jobs:
            writer.writerow([
                job.job_id,
                job.user_name,
                job.user_id,
                job.file_name,
                job.status,
                job.created_at,
                job.pages,
            ])

    return len(new_jobs)