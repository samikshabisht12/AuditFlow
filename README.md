# AuditFlow: Data Pipeline and Analytics

AuditFlow is a comprehensive data automation and backend infrastructure solution designed for public sector audit analytics. It orchestrates the extraction, cleaning, validation, and visualization of structured data, ensuring robust analysis and reporting.

The system is engineered for resilience, capable of functioning seamlessly even when optional services (such as external databases or cloud storage) are unconfigured. In such scenarios, AuditFlow defaults to a demonstration mode using sample datasets.

## Architecture and Core Capabilities

1. **Data Extraction**: Automated retrieval of state-wise data from public portals.
2. **Data Standardization**: Comprehensive cleaning and normalization of raw records.
3. **Metric Calculation**: Computation of key performance indicators, such as utilization rates, and the assignment of risk categories based on predefined thresholds.
4. **Data Validation**: Rigorous quality assurance checks to identify and highlight data anomalies.
5. **Persistent Storage**: Configurable integration with PostgreSQL for reliable data retention.
6. **Cloud Backup**: Automated synchronization with AWS S3 for secure, off-site data archiving.
7. **Data Accessibility**: RESTful API endpoints and a dynamic dashboard for real-time data access and visualization.

## Technology Stack

- **Language**: Python
- **Data Extraction**: Requests, BeautifulSoup, Selenium
- **Data Processing**: Pandas, NumPy
- **API Framework**: Flask
- **Visualization**: Plotly Dash
- **Database**: PostgreSQL, SQLAlchemy
- **Cloud Integration**: AWS S3, Boto3
- **Configuration**: python-dotenv

## Project Structure

```text
AuditFlow/
|- main.py                    # End-to-end pipeline entrypoint
|- requirements.txt           # Project dependencies
|- .env.example               # Environment variables template
|- api/
|  |- app.py                  # Flask REST API
|- cloud/
|  |- s3_upload.py            # AWS S3 integration module
|- dashboard/
|  |- dashboard.py            # Plotly Dash analytics interface
|- data/
|  |- cleaner.py              # Data cleaning and validation logic
|- database/
|  |- db_connect.py           # PostgreSQL connection and queries
|- scraper/
|  |- nrega_scraper.py        # Primary data scraping module
|  |- scheduler.py            # Automated job scheduling
|  |- selenium_scraper.py     # Selenium-based fallback scraper
```

## Setup and Installation

### 1. Environment Preparation

It is recommended to use a virtual environment to manage dependencies.

**Windows PowerShell:**
```powershell
python -m venv venv
./venv/Scripts/Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the provided environment template and configure your local settings.

```powershell
cp .env.example .env
```

Ensure the following variables are defined in your `.env` file:

**Database Configuration (Optional)**
- `DB_USER`
- `DB_PASS`
- `DB_HOST`
- `DB_NAME`

**AWS S3 Configuration (Optional)**
- `AWS_ACCESS_KEY`
- `AWS_SECRET_KEY`
- `S3_BUCKET`

**API Authentication Keys**
- `ADMIN_API_KEY`
- `AUDITOR_API_KEY`
- `VIEWER_API_KEY`

*Note: If database or AWS variables are omitted, the application will automatically fall back to demonstration mode.*

## Running the Application

### Full Pipeline Execution

Execute the entire data pipeline, including extraction, cleaning, validation, database storage, and cloud backup.

```powershell
python main.py
```

### REST API Service

Launch the Flask REST API server to serve processed data.

```powershell
python api/app.py
```
The API will be available at: `http://127.0.0.1:5000`

### Analytics Dashboard

Start the Plotly Dash interactive dashboard.

```powershell
python dashboard/dashboard.py
```
The dashboard will be available at: `http://127.0.0.1:8050`

### Scheduled Execution

Run the pipeline on a scheduled basis.

```powershell
python scraper/scheduler.py
```

## API Endpoints

Authentication is required for most endpoints via the `X-API-Key` header.

- `GET /api/health`: System status (No authentication required)
- `GET /api/nrega/summary`: General data summary (Requires valid API key)
- `GET /api/nrega/anomalies`: Flagged anomalies (Requires Admin or Auditor API key)
- `GET /api/nrega/state/<state_name>`: State-specific records (Requires valid API key)
- `GET /api/nrega/validation-report`: Complete validation report (Requires valid API key)

**Example Request:**
```powershell
curl -H "X-API-Key: your_admin_key_here" http://127.0.0.1:5000/api/nrega/summary
```