# 🖨️ Printer Count Automate

Automated scraping and data integration system for Ricoh Web Image Monitor.

This project extracts:
- 📄 **Printer Job History** (transaction-level data)
- 📊 **Counter per User** (summary-level data)

…and syncs them into:
- CSV (for audit & backup)
- Microsoft Access (for reporting & analytics)

---

## 🚀 Key Features

### ✅ 1. Printer Job History Scraping
- Multi-page scraping with pagination handling
- Deduplication using row fingerprint
- Captures:
  - Job ID
  - User Name / ID
  - File Name
  - Status
  - Created At
  - Pages

---

### ✅ 2. Counter per User Scraping
- Extracts user-level print usage
- No pagination required
- Captures:
  - Total Prints (B&W)
  - Total Prints (Color)
  - Total Prints (Auto-calculated)
  - Printer B&W usage
  - Last update timestamp

---

### ✅ 3. Microsoft Access Integration
- Inserts new job records into `PrinterHistoryT`
- Updates user totals in `EmployeeT`
- Uses:
  - `RowFingerprint` → prevent duplicate inserts
  - `PrinterID` → match user for updates

---

### ✅ 4. ESG & Digitalisation Alignment 🌱
- Reduces manual monitoring
- Enables print usage tracking
- Supports sustainability reporting:
  - paper consumption
  - user-level print accountability
- Promotes digital workflow adoption

---

## 🧱 Project Structure

```bash
printer-count-automate/
├── config/
│   └── settings.py
│
├── logs/
│
├── models/
│   └── print_job.py
│
├── services/
│   ├── ingestion_service.py      # Main workflow orchestrator
│   ├── ricoh_browser.py          # Navigation & login handling
│   └── ricoh_scraper.py          # Data extraction logic
│
├── utils/
│   ├── access_utils.py           # MS Access integration
│   ├── csv_utils.py              # CSV handling
│   ├── state_utils.py
│   └── time_utils.py
│
├── .env                          # Environment variables
├── app.py                        # Entry point
├── run_print_history.bat         # Windows scheduler runner
├── requirements.txt
└── README.md
```
---
## ⚙️ Setup Instructions

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Install Playwright
```bash
playwright install
```

### 3️⃣ Setup ```env.``` file

Create a ```.env``` file in the project root:

```bash
TZ=Asia/Kuala_Lumpur

PRINTER_BASE_URL=http://YourIPAddress
LOGIN_USER= YourUsername
LOGIN_PASS= YOurPassword

HEADLESS=true
POLL_SECONDS=300

CSV_PATH=C:\YourPath\printer_history.csv
ACCESS_DB_PATH=C:\YourPath\database.accdb

MAX_PAGES=50
```

### 4️⃣ MS Access Requirements

Ensure the following table structures exist.

🧾 ```PrinterHistoryT```

| Field | Description |
| -------- | -------- |
| ```CreatedDate```  | Print timestamp   |
| ```UserName```	| User name |
| ```UserId``` |	Printer ID |
| ```FileName``` |	Document name |
| ```Status```	| Print status |
| ```Pages``` |	Page count |
| ```RowFingerprint``` |	Deduplication key |

---

👤 ```EmployeeT```

| Field | Description |
| -------- | -------- |
| ```PrinterID``` |	User ID matching Ricoh User |
| ```TotalPrints```	| Total prints (B&W + Color) |
| ```TotalPrintsBW```	| Total prints B&W |
| ```TotalPrintsColor``` |	Total prints Color |
| ```PrinterBW``` |	Printer Black & White usage |
| ```TotalPrintUpdateTime``` |	Last sync timestamp |

---

### ▶️ Running the Project

1️⃣ Run manually
```bash
python app.py
```

2️⃣ Run via Windows Scheduler

Use the provided batch file:
```bash
run_print_history.bat
```
---
### 🔄 Process Flow

1. Login to Ricoh Web UI
2. Navigate to Printer Job History
3. Scrape all pages
4. Save data to CSV and Access
5. Click Home
6. Navigate to Counter per User
7. Set Display Count = 20
8. Scrape user totals
9. Update EmployeeT in Access

---
### 🧠 Data Logic

✔ Printer Job History
- Insert only new records
- Prevent duplicates using RowFingerprint

✔ Counter per User
- Always overwrite the latest totals
- Do not accumulate values across runs

```TotalPrints = TotalPrintsBW + TotalPrintsColor```

---

### 🛠 Tech Stack

- Python 3.11+
- Playwright (browser automation)
- Microsoft Access (ODBC)
- CSV (backup layer)