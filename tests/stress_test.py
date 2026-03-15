import unittest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import os
import multiprocessing
import sys

# Standardize pathing so imports work from anywhere
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

# Import app components inside a protected block to avoid side-effects
try:
    from app import app, db, DATA_DIR, VERSION
except ImportError as e:
    print(f"CRITICAL: Failed to import app components: {e}")
    sys.exit(1)

def run_flask():
    app.config['DEBUG'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test_ojt_tracker.db"
    app.run(host='127.0.0.1', port=8080, debug=False, use_reloader=False)

class KitchenNightmaresTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Fresh test DB (Isolated!)
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test_ojt_tracker.db"
        with app.app_context():
            db.drop_all()
            db.create_all()
            
        cls.flask_process = multiprocessing.Process(target=run_flask)
        cls.flask_process.start()
        time.sleep(5) # Give it plenty of time to warm up
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        cls.base_url = "http://127.0.0.1:8080"

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        if hasattr(cls, 'flask_process'):
            cls.flask_process.terminate()
            cls.flask_process.join()

    def wait_for_element(self, selector, by=By.CSS_SELECTOR, timeout=10):
        return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located((by, selector)))

    def test_01_ui_boot_check(self):
        """Case 0: UI Version & Dashboard Boot"""
        self.driver.get(self.base_url)
        # Wait for the explicit version ID
        version_tag = self.wait_for_element("#sidebar-version-tag", by=By.ID, timeout=15)
        print(f"DEBUG: Found Version Tag: {version_tag.text}")
        self.assertIn("v1.3.0", version_tag.text)

    def test_02_target_hours_zero(self):
        """Case 1: Target Hours = 0"""
        settings_btn = self.wait_for_element("button[onclick*='SettingsModal']")
        settings_btn.click()
        
        target_input = self.wait_for_element("#targetHours")
        target_input.clear()
        target_input.send_keys("0")
        
        save_btn = self.driver.find_element(By.CSS_SELECTOR, "button[onclick='saveSettings()']")
        save_btn.click()
        time.sleep(1)
        
        end_date = self.driver.find_element(By.ID, "projectedEndDate").text
        print(f"DEBUG: Projected End Date for 0 hrs: {end_date}")
        self.assertTrue(len(end_date) > 0)

    def test_03_negative_hours(self):
        """Case 2: Target Hours = -50"""
        self.driver.get(self.base_url) # Reset
        settings_btn = self.wait_for_element("button[onclick*='SettingsModal']")
        settings_btn.click()
        
        target_input = self.wait_for_element("#targetHours")
        target_input.clear()
        target_input.send_keys("-50")
        
        self.driver.find_element(By.CSS_SELECTOR, "button[onclick='saveSettings()']").click()
        time.sleep(1)
        
        end_date = self.driver.find_element(By.ID, "projectedEndDate").text
        print(f"DEBUG: Projected End Date for -50 hrs: {end_date}")
        self.assertTrue(len(end_date) > 0)

    # Note: Full 30 cases would expand here...
    
if __name__ == "__main__":
    print("\n🍳 GORDON RAMSAY'S KITCHEN NIGHTMARES STRESS TEST (v1.3.0) 🍳")
    print("============================================================")
    unittest.main(verbosity=2)
