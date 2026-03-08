import time

from config.settings import POLL_SECONDS
from services.ingestion_service import run_ingestion

def main():
    print("Ricoh scraping engine started...")

    while True:
        try:
            run_ingestion()
        except Exception as e:
            print(f"Scheduler error: {e}")

        print(f"Sleeping for {POLL_SECONDS} seconds...\n")
        time.sleep(POLL_SECONDS)

if __name__ == "__main__":
    main()