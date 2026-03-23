from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import json
import sys

def scrape_ph_holidays(year):
    """
    Scrapes the Philippine holidays from timeanddate.com for a given year using Selenium.
    Returns a list of dictionaries containing date and name.
    """
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Optional: spoof user agent to avoid basic blocks
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    try:
        driver = webdriver.Chrome(options=options)
    except Exception as e:
        print(json.dumps({"error": f"Failed to initialize Chrome Driver: {str(e)}"}))
        return []

    url = f"https://www.timeanddate.com/holidays/philippines/{year}"
    holidays = []
    
    try:
        driver.get(url)
        # Give the table time to render fully
        time.sleep(2)
        
        # Scrape the table body
        table = driver.find_element(By.ID, "holidays-table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        for row in rows:
            # Skip header or hidden rows
            row_class = row.get_attribute("class")
            if row_class and ("head" in row_class or "sep" in row_class):
                continue
                
            style = row.get_attribute("style")
            if style and "display: none" in style:
                continue

            th_elements = row.find_elements(By.TAG_NAME, "th")
            td_elements = row.find_elements(By.TAG_NAME, "td")
            
            if th_elements and td_elements:
                date_str_raw = th_elements[0].text.strip()
                # Table usually has: Date (th), Day (td[0]), Name (td[1]), Type (td[2])
                name_idx = 1 if len(td_elements) > 1 else 0
                name_raw = td_elements[name_idx].text.strip()
                
                if date_str_raw and name_raw:
                    clean_date_str = f"{date_str_raw} {year}"
                    date_obj = None
                    
                    # Try common formats found on timeanddate.com
                    for fmt in ["%b %d %Y", "%d %b %Y", "%B %d %Y", "%d %B %Y"]:
                        try:
                            date_obj = datetime.strptime(clean_date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                    
                    if date_obj:
                        holidays.append({
                            "date": date_obj.strftime("%Y-%m-%d"),
                            "name": name_raw
                        })

    except Exception as e:
        print(json.dumps({"error": f"Scraper failure: {str(e)}"}))
        driver.quit()
        return []

    finally:
        driver.quit()
        
    return holidays

if __name__ == "__main__":
    target_year = datetime.now().year
    
    # If a year arg is provided, use it
    if len(sys.argv) > 1:
        try:
            target_year = int(sys.argv[1])
        except ValueError:
            pass
            
    h_list = scrape_ph_holidays(target_year)
    print(json.dumps({"status": "success", "year": target_year, "holidays": h_list}))
