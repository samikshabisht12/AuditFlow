import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def scrape_nrega_statewise():
    url = "https://nreganet.nic.in/netnrega/Sch_State.aspx"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"id": "GridView1"})
        rows = []
        if table:
            for tr in table.find_all("tr")[1:]:
                cols = [td.get_text(strip=True) for td in tr.find_all("td")]
                if cols:
                    rows.append(cols)
        df = pd.DataFrame(rows, columns=[
            "state", "registered_workers", "job_cards_issued",
            "households_worked", "person_days_generated"
        ])
        df["scraped_at"] = datetime.now()
        df["source"] = "NREGA_PUBLIC_PORTAL"
        print(f"Successfully scraped {len(df)} records from NREGA portal")
        return df
    except Exception as e:
        print(f"Live scraping failed ({e}), using sample data instead")
        return get_sample_data()


def get_sample_data():
    data = {
        "state": [
            "Jammu & Kashmir", "Rajasthan", "Uttar Pradesh",
            "Bihar", "Madhya Pradesh", "Jharkhand",
            "West Bengal", "Andhra Pradesh", "Tamil Nadu", "Gujarat"
        ],
        "registered_workers": [
            850000, 12000000, 25000000, 18000000, 14000000,
            8000000, 16000000, 11000000, 9000000, 7000000
        ],
        "job_cards_issued": [
            420000, 9800000, 19000000, 14500000, 11000000,
            6500000, 13000000, 9200000, 7500000, 5800000
        ],
        "households_worked": [
            90000, 7200000, 13000000, 9800000, 8200000,
            5100000, 10000000, 7000000, 5800000, 3200000
        ],
        "person_days_generated": [
            1200000, 180000000, 310000000, 220000000, 190000000,
            120000000, 240000000, 160000000, 130000000, 80000000
        ],
        "scraped_at": [datetime.now()] * 10,
        "source": ["SAMPLE_DATA"] * 10
    }
    return pd.DataFrame(data)