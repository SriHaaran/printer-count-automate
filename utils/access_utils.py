import os
from datetime import datetime
from typing import List, Optional, Set

import pyodbc

from models.print_job import PrintJob
from utils.csv_utils import build_row_fingerprint

def get_access_connection(db_path: str):
    """
    Create a connection to MS Access database.
    Requires Microsoft Access Database Engine driver on Windows.
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Access database not found: {db_path}")

    conn_str = (
        r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
        rf"DBQ={db_path};"
    )
    return pyodbc.connect(conn_str)

def load_existing_fingerprints_from_access(db_path: str) -> Set[str]:
    """
    Load stored fingerprints from Access to avoid duplicate inserts.
    """
    conn = get_access_connection(db_path)
    cursor = conn.cursor()

    fingerprints: Set[str] = set()

    cursor.execute("SELECT RowFingerprint FROM PrinterHistoryT")

    for row in cursor.fetchall():
        value = (row[0] or "").strip()
        if value:
            fingerprints.add(value)

    cursor.close()
    conn.close()

    return fingerprints

def insert_new_jobs_to_access(db_path: str, jobs: List[PrintJob]) -> int:
    """
    Insert new jobs into PrinterHistoryT table.
    """
    existing_fingerprints = load_existing_fingerprints_from_access(db_path)

    conn = get_access_connection(db_path)
    cursor = conn.cursor()

    inserted = 0

    for job in jobs:

        fp = build_row_fingerprint(job)

        if fp in existing_fingerprints:
            continue

        cursor.execute(
            """
            INSERT INTO PrinterHistoryT
            (CreatedDate, UserName, UserId, FileName, Status, Pages, Description, RowFingerprint)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job.created_at,
                job.user_name,
                job.user_id,
                job.file_name,
                job.status,
                job.pages,
                "",  # leave description empty
                fp,
            )
        )

        existing_fingerprints.add(fp)
        inserted += 1

    conn.commit()
    cursor.close()
    conn.close()

    return inserted