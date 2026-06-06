import sys
import os
from datetime import datetime

from scraper.nrega_scraper import scrape_nrega_statewise
from data.cleaner import clean_nrega_data, validate_data
from cloud.s3_upload import upload_dataframe_to_s3

try:
    from database.db_connect import create_tables, save_to_db, log_pipeline_run
    DB_AVAILABLE = True
except Exception:
    DB_AVAILABLE = False

def run_full_pipeline():
    print("\n" + "="*60)
    print("  AG AUDIT J&K — DATA PIPELINE")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    print("\n📥 STEP 1: Scraping NREGA data...")
    df_raw = scrape_nrega_statewise()
    print(f"   → {len(df_raw)} raw records collected")

    print("\n🧹 STEP 2: Cleaning data...")
    df_clean = clean_nrega_data(df_raw)
    print(f"   → {len(df_clean)} clean records ready")

    print("\n✅ STEP 3: Validating data quality...")
    report = validate_data(df_clean)
    if report["passed"]:
        print("   → All validation checks PASSED")
    else:
        print(f"   → {report['issues_found']} issues found:")
        for issue in report["issues"]:
            print(f"      ⚠️  {issue}")

    if DB_AVAILABLE:
        print("\n💾 STEP 4: Storing in PostgreSQL database...")
        try:
            create_tables()
            save_to_db(df_clean)
            log_pipeline_run(
                action="FULL_PIPELINE_RUN",
                records=len(df_clean),
                issues=report["issues"],
                status="SUCCESS" if report["passed"] else "COMPLETED_WITH_FLAGS"
            )
        except Exception as e:
            print(f"   → Database error: {e}")
            print("   → Database not connected — running in demo mode")
    else:
        print("\n💾 STEP 4: Database not connected — running in demo mode")

    print("\n☁️  STEP 5: Backing up to cloud storage (AWS S3)...")
    s3_path = upload_dataframe_to_s3(df_clean, "nrega_data")

    print("\n" + "="*60)
    print("  PIPELINE COMPLETE")
    print(f"  Records processed : {len(df_clean)}")
    print(f"  Issues flagged    : {report['issues_found']}")
    print(f"  High risk states  : {len(df_clean[df_clean['risk_flag'] == 'HIGH RISK'])}")
    print(f"  Cloud backup      : {s3_path}")
    print(f"  Finished          : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    print("\n📊 SAMPLE OUTPUT:")
    print(df_clean[["state", "utilization_rate", "risk_flag"]].to_string(index=False))

    return df_clean

if __name__ == "__main__":
    run_full_pipeline()