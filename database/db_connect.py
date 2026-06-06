import psycopg2
from sqlalchemy import create_engine, text
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    db_url = (
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
        f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(db_url)


def create_tables():
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS nrega_data (
                id SERIAL PRIMARY KEY,
                state VARCHAR(100) NOT NULL,
                registered_workers BIGINT DEFAULT 0,
                job_cards_issued BIGINT DEFAULT 0,
                households_worked BIGINT DEFAULT 0,
                person_days_generated BIGINT DEFAULT 0,
                utilization_rate FLOAT DEFAULT 0,
                avg_person_days FLOAT DEFAULT 0,
                risk_flag VARCHAR(20),
                source VARCHAR(50),
                scraped_at TIMESTAMP,
                cleaned_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                action VARCHAR(100),
                records_processed INT,
                issues_found TEXT,
                status VARCHAR(20),
                run_at TIMESTAMP DEFAULT NOW()
            );
        """))
        conn.commit()
    print("  Database tables ready ✅")


def save_to_db(df: pd.DataFrame, table: str = "nrega_data"):
    engine = get_engine()
    df.to_sql(table, engine, if_exists="append", index=False)
    print(f"  Saved {len(df)} records to '{table}' table ✅")


def log_pipeline_run(action, records, issues, status):
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO audit_log (action, records_processed, issues_found, status)
            VALUES (:action, :records, :issues, :status)
        """), {
            "action": action,
            "records": records,
            "issues": str(issues),
            "status": status
        })
        conn.commit()


def fetch_from_db(query: str, params: dict = None) -> pd.DataFrame:
    engine = get_engine()
    return pd.read_sql(text(query), engine, params=params)