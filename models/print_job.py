from dataclasses import dataclass

@dataclass
class PrintJob:
    job_id: str
    user_name: str
    user_id: str
    file_name: str
    status: str
    created_at: str
    pages: str