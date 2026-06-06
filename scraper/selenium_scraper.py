import pandas as pd

def scrape_with_selenium(url):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(options=options)
    records = []
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows[1:]:
            cols = [col.text.strip() for col in row.find_elements(By.TAG_NAME, "td")]
            if cols:
                records.append(cols)
        print(f"Selenium scraped {len(records)} records")
        return pd.DataFrame(records)
    except Exception as e:
        print(f"Selenium error: {e}")
        return pd.DataFrame()
    finally:
        driver.quit()
