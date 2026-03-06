from dataclasses import dataclass

@dataclass
class PrintJob:
    job_id: str
    user_id: str
    file_name: str
    created_at: str