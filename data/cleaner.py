import pandas as pd
import numpy as np
from datetime import datetime

def clean_nrega_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    print(f"  Starting with {len(df)} raw records...")
    
    before = len(df)
    df.drop_duplicates(subset=["state"], keep="last", inplace=True)
    print(f"  Removed {before - len(df)} duplicate rows")
    
    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()
    
    numeric_cols = [
        "registered_workers", "job_cards_issued",
        "households_worked", "person_days_generated"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "")
                .str.replace("-", "0")
                .str.strip()
                .pipe(pd.to_numeric, errors="coerce")
                .fillna(0)
                .astype(int)
            )
    
    state_map = {
        "J&K": "Jammu & Kashmir",
        "J & K": "Jammu & Kashmir",
        "UP": "Uttar Pradesh",
        "MP": "Madhya Pradesh",
    }
    df["state"] = df["state"].replace(state_map)
    
    df["utilization_rate"] = np.where(
        df["job_cards_issued"] > 0,
        (df["households_worked"] / df["job_cards_issued"] * 100).round(2),
        0
    )
    
    df["avg_person_days"] = np.where(
        df["households_worked"] > 0,
        (df["person_days_generated"] / df["households_worked"]).round(1),
        0
    )
    
    df["risk_flag"] = df["utilization_rate"].apply(
        lambda x: "HIGH RISK" if x < 30 else ("MEDIUM RISK" if x < 60 else "NORMAL")
    )
    
    df["cleaned_at"] = datetime.now()
    print(f"  Cleaning complete. {len(df)} clean records ready.")
    return df


def validate_data(df: pd.DataFrame) -> dict:
    issues = []
    
    for col in ["state", "registered_workers"]:
        nulls = df[col].isnull().sum()
        if nulls > 0:
            issues.append(f"Missing values in '{col}': {nulls} rows affected")
    
    if "households_worked" in df.columns and "job_cards_issued" in df.columns:
        anomalies = df[df["households_worked"] > df["job_cards_issued"]]
        if len(anomalies) > 0:
            issues.append(f"Logical error - workers > job cards in: {list(anomalies['state'])}")
    
    if "utilization_rate" in df.columns:
        high_risk = df[df["utilization_rate"] < 30]
        if len(high_risk) > 0:
            issues.append(f"High risk states (utilization < 30%): {list(high_risk['state'])}")
    
    for col in ["registered_workers", "job_cards_issued"]:
        if col in df.columns:
            negatives = df[df[col] < 0]
            if len(negatives) > 0:
                issues.append(f"Negative values found in '{col}'")
    
    return {
        "total_records": len(df),
        "issues_found": len(issues),
        "issues": issues,
        "passed": len(issues) == 0,
        "validated_at": str(datetime.now())
    }