import schedule
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import run_full_pipeline

def job():
    print("Running scheduled AuditFlow pipeline...")
    run_full_pipeline()

if __name__ == "__main__":
    # Schedule to run daily at 2:00 AM
    schedule.every().day.at("02:00").do(job)
    
    print("Scheduler started. Waiting for jobs...")
    while True:
        schedule.run_pending()
        time.sleep(60)
