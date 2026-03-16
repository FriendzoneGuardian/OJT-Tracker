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
from datetime import datetime, timedelta

class ClockworkStressTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        cls.base_url = "http://127.0.0.1:8080"
        
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_night_owl_calculation(self):
        """Test 17:00 to 02:00 with Night Owl toggled ON."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 15)
        
        log_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick*='toggleModal(true)']")))
        log_btn.click()
        
        wait.until(EC.visibility_of_element_located((By.ID, "entry-modal")))
        
        # Set a unique date
        unique_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        self.driver.execute_script(f"document.getElementById('date').value = '{unique_date}'")
        
        # Use send_keys for time inputs (cleaner than execute_script for some drivers)
        m_in = self.driver.find_element(By.ID, "morn_in")
        m_in.send_keys("17:00")
        
        a_out = self.driver.find_element(By.ID, "aftie_out")
        a_out.send_keys("02:00")
        
        # Toggle Night Owl
        night_toggle = self.driver.find_element(By.ID, "is_night_shift")
        if not night_toggle.is_selected():
            self.driver.execute_script("arguments[0].click();", night_toggle)
            
        # Debug: check values
        print(f"DEBUG: Night Owl values - In: {m_in.get_attribute('value')}, Out: {a_out.get_attribute('value')}")
            
        # Save
        save_btn = self.driver.find_element(By.CSS_SELECTOR, "#entry-form button[type='submit']")
        save_btn.click()
        
        # Wait for modal to close
        wait.until(EC.invisibility_of_element_located((By.ID, "entry-modal")))
        time.sleep(2) 
        
        # 17:00 to 02:00 is 9 hours. Default cap is 8.0h.
        row = wait.until(EC.presence_of_element_located((By.XPATH, f"//tr[contains(., '{unique_date}')]")))
        self.assertIn("8.0h", row.text, f"Night Owl shift without overtime should be capped at 8.0h. Got: {row.text}")

    def test_auto_normalization(self):
        """Test '1:00' in Afternoon field is treated as 13:00."""
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 15)
        
        log_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[onclick*='toggleModal(true)']")))
        log_btn.click()
        
        norm_date = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
        
        wait.until(EC.visibility_of_element_located((By.ID, "entry-modal")))
        self.driver.execute_script(f"document.getElementById('date').value = '{norm_date}'")
        
        a_in = self.driver.find_element(By.ID, "aftie_in")
        a_in.send_keys("01:00") # Expect 13:00
        
        a_out = self.driver.find_element(By.ID, "aftie_out")
        a_out.send_keys("05:00") # Expect 17:00
        
        print(f"DEBUG: Norm values - In: {a_in.get_attribute('value')}, Out: {a_out.get_attribute('value')}")
        
        save_btn = self.driver.find_element(By.CSS_SELECTOR, "#entry-form button[type='submit']")
        save_btn.click()
        
        wait.until(EC.invisibility_of_element_located((By.ID, "entry-modal")))
        time.sleep(2)
        
        # 13:00 to 17:00 = 4.0h
        row = wait.until(EC.presence_of_element_located((By.XPATH, f"//tr[contains(., '{norm_date}')]")))
        self.assertIn("4.0h", row.text, f"Afternoon 1:00-5:00 should normalize to 4.0 hours. Got: {row.text}")

if __name__ == "__main__":
    unittest.main()
