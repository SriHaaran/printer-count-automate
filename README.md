# Ricoh MPC3504 – Printer Job History Automation

## Overview

This service automates extraction of **Printer Job History** from a Ricoh MPC3504 (Web Image Monitor), processes the data based on time windows, and stores structured output in daily Excel files.

Key capabilities:

- Login via browser automation (Playwright)
- Supports Ricoh **Frames-based UI**
- Handles **pagination across job history pages**
- Extracts only records within defined time windows
- Creates **daily Excel file**
- Splits records into **separate sheets per UserID**
- Leaves Description column blank (for staff input)
- Docker-ready deployment
- Stateful deduplication using JobID

---

# Project Architecture

This project follows a clean, modular service architecture.

## Folder Structure Explanation

## 1️⃣ app.py
Main entry point (orchestrator only).

Responsibilities:
- Controls execution loop
- Determines working hours vs after-hours logic
- Computes time window
- Calls service layer
- Writes to Excel
- Saves state
- Controls polling interval

It does NOT contain scraping or Excel logic directly.

---
## 2️⃣ config/

### settings.py

Centralized configuration loaded from environment variables.

Contains:
- Printer base URL
- Login credentials
- Working hour definitions
- Poll intervals
- Time window buffer
- Output and state directories
- Headless mode flag
- Timezone

This keeps configuration separate from logic.

---

## 3️⃣ models/

### print_job.py

Defines the data structure for a print job.

```Python
@dataclass
class PrintJob:
    job_id: str
    user_id: str
    file_name: str
    created_at: str
```
---
## 4️⃣ services/

Business logic layer.

### ricoh_browser.py

Handles:
- Login
- Navigation
- Frame detection
- Moving to Printer Job History page

This isolates browser automation from scraping logic.

### ricoh_scraper.py

Handles:
- Table parsing
- Frame scraping
- Pagination
- Time filtering
- JobID extraction
- Ricoh datetime parsing

Only responsible for extracting structured PrintJob objects.

### scheduler.py (optional future)

Reserved for:
- Advanced scheduling logic
- Cron-style execution
- Retry strategies

## 5️⃣ utils/

Reusable helper logic.

### time_utils.py
- Working hours detection
- Poll interval decision
- Time window computation
- Window buffer logic

### excel_utils.py

- Excel creation
- Daily folder creation
- Sheet per UserID
- Description column intentionally blank
- Safe sheet naming

### state_utils.py

- JSON-based state management
- Deduplication by JobID
- Daily state file

State files stored under:
`state/state_YYYY-MM-DD.json`

---
## 6️⃣ output/

Stores generated Excel files.

Structure:
```
output/
   2026-03-03/
       PrinterJobHistory_2026-03-03.xlsx
   2026-03-04/
       PrinterJobHistory_2026-03-04.xlsx
```

Each Excel file contains:
- Separate sheet per UserID
- Columns:
  - UserID
  - File Name
  - Description (blank)
  - Created at

---
## 7️⃣ state/

Stores daily deduplication state.

Example:
`state/state_2026-03-03.json`

Used to:
- Prevent duplicate insertion
- Track processed JobID values
- Maintain lightweight history
---
## Execution Logic
### Working Hours

Default:
- 08:00 to 17:00

During working hours:
- Poll every 5 minutes
- Window = 5 minutes + buffer

After working hours:
- Poll every 30 minutes
- Window = 30 minutes + buffer
---
## Time Window Logic

Instead of relying only on JobID, the system:

1. Calculates:
```
window_start = now - interval - buffer
window_end = now
```
2. Scrapes page 1

3. Checks Created At timestamp

4. If oldest record on page still within window → go to next page

5. Stops when:
- Oldest record < window_start
- No next page available
- Safety page limit reached

This ensures no missed records due to pagination.

---

## Frame Handling

Ricoh Web Image Monitor uses HTML frames.

The system:
- Iterates through page.frames
- Detects the frame containing table.reportListCommon
- Executes scraping inside the correct frame context