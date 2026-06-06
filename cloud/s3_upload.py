import boto3
import pandas as pd
import io
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY", "demo-key"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY", "demo-secret"),
        region_name="ap-south-1"
    )

def upload_dataframe_to_s3(df: pd.DataFrame, filename_prefix: str) -> str:
    bucket = os.getenv("S3_BUCKET", "audit-data-bucket")
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    today = datetime.now()
    key = f"audit-data/{today.year}/{today.month:02d}/{filename_prefix}_{today.strftime('%Y%m%d_%H%M')}.csv"
    
    if not os.getenv("AWS_ACCESS_KEY"):
        print("  [Info] S3 skipped (demo mode - no AWS credentials configured)")
        return f"demo-path/{key}"

    try:
        s3 = get_s3_client()
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=csv_buffer.getvalue(),
            ServerSideEncryption="AES256",
            Metadata={
                "uploaded-by": "ag-audit-jk-pipeline",
                "records": str(len(df)),
                "upload-date": str(today)
            }
        )
        print(f"  [Success] Uploaded to S3: s3://{bucket}/{key}")
        return key
    except Exception as e:
        print(f"  [Warning] S3 upload failed: {e}")
        return f"demo-path/{key}"


def list_audit_files(prefix="audit-data/"):
    s3 = get_s3_client()
    try:
        response = s3.list_objects_v2(
            Bucket=os.getenv("S3_BUCKET", "audit-data-bucket"),
            Prefix=prefix
        )
        files = [obj["Key"] for obj in response.get("Contents", [])]
        return files
    except Exception as e:
        print(f"  [Info] Cannot list S3 files in demo mode: {e}")
        return []