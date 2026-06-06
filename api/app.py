from flask import Flask, jsonify, request
from functools import wraps
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.cleaner import clean_nrega_data, validate_data
from scraper.nrega_scraper import get_sample_data

app = Flask(__name__)

from dotenv import load_dotenv

load_dotenv()

API_KEYS = {
    os.getenv("ADMIN_API_KEY", "admin-key-001"): "admin",
    os.getenv("AUDITOR_API_KEY", "audit-key-002"): "auditor",
    os.getenv("VIEWER_API_KEY", "read-key-003"): "viewer"
}

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if not key or key not in API_KEYS:
            return jsonify({
                "error": "Unauthorized",
                "message": "Valid API key required in X-API-Key header"
            }), 401
        request.user_role = API_KEYS[key]
        return f(*args, **kwargs)
    return decorated


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "running",
        "service": "AG Audit J&K Analytics API",
        "version": "1.0"
    })


@app.route("/api/nrega/summary", methods=["GET"])
@require_api_key
def nrega_summary():
    try:
        from database.db_connect import fetch_from_db
        df = fetch_from_db("SELECT * FROM nrega_data ORDER BY scraped_at DESC LIMIT 100")
    except Exception:
        df = clean_nrega_data(get_sample_data())
    return jsonify({
        "status": "success",
        "role": request.user_role,
        "total_records": len(df),
        "data": df.to_dict(orient="records")
    })


@app.route("/api/nrega/anomalies", methods=["GET"])
@require_api_key
def get_anomalies():
    if request.user_role == "viewer":
        return jsonify({"error": "Insufficient permissions"}), 403
    try:
        from database.db_connect import fetch_from_db
        df = fetch_from_db("""
            SELECT state, utilization_rate, households_worked,
                   job_cards_issued, risk_flag, scraped_at
            FROM nrega_data WHERE risk_flag = 'HIGH RISK'
            ORDER BY utilization_rate ASC
        """)
    except Exception:
        df = clean_nrega_data(get_sample_data())
        df = df[df["risk_flag"] == "HIGH RISK"]
    return jsonify({
        "status": "success",
        "audit_flag": "LOW_UTILIZATION_RISK",
        "count": len(df),
        "records": df.to_dict(orient="records")
    })


@app.route("/api/nrega/state/<state_name>", methods=["GET"])
@require_api_key
def get_state(state_name):
    try:
        from database.db_connect import fetch_from_db
        df = fetch_from_db("""
            SELECT * FROM nrega_data
            WHERE LOWER(state) LIKE LOWER(:state)
            ORDER BY scraped_at DESC LIMIT 10
        """, params={"state": f"%{state_name}%"})
    except Exception:
        df = clean_nrega_data(get_sample_data())
        df = df[df["state"].str.lower().str.contains(state_name.lower())]
    if df.empty:
        return jsonify({"error": f"No data found for state: {state_name}"}), 404
    return jsonify({
        "status": "success",
        "state": state_name,
        "records": df.to_dict(orient="records")
    })


@app.route("/api/nrega/validation-report", methods=["GET"])
@require_api_key
def validation_report():
    df = clean_nrega_data(get_sample_data())
    report = validate_data(df)
    return jsonify(report)


if __name__ == "__main__":
    print("Starting AG Audit J&K REST API...")
    print("Endpoints:")
    print("  GET /api/health")
    print("  GET /api/nrega/summary        [requires API key]")
    print("  GET /api/nrega/anomalies      [requires admin/auditor key]")
    print("  GET /api/nrega/state/<name>   [requires API key]")
    print("  GET /api/nrega/validation-report [requires API key]")
    app.run(debug=True, port=5000)