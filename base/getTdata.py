import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from base.browser import Browser
from selenium.webdriver.support import expected_conditions as EC
import sys
from selenium.webdriver.support.ui import WebDriverWait

class tData(Browser):
    def __init__(self, browser_instance):
        super().__init__(browser_instance)

    def delay(self, seconds):
        time.sleep(seconds)

    def ask_question(self, query):
        return input(query)

    def resource_path(self, relative_path):
        """ Get the absolute path to the resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def load_local_storage(self, session_id):
        localstorage_path = self.resource_path("data/authLogin/localstorage.json")
        
        if os.path.exists(localstorage_path):
            try:
                with open(localstorage_path, "r") as file:
                    data = json.load(file)

                session = next((entry for entry in data if entry["id"] == session_id), None)

                if not session:
                    print(f'Session with id "{session_id}" not found.')
                    return False

                local_storage = session["data"]["localStorage"]
                for key, value in local_storage.items():
                    self.browser.execute_script(f"window.localStorage.setItem('{key}', '{value}');")
                
                return True
            except Exception as e:
                print(f"Error loading localstorage.json: {e}")
                return False
        else:
            print("File localstorage.json not found.")
            return False

    def save_local_storage(self, session_id):
        localstorage_path = self.resource_path("data/authLogin/localstorage.json")
        
        try:
            local_storage_data = self.browser.execute_script("""    
                let data = {};
                for (let i = 0; i < window.localStorage.length; i++) {
                    let key = window.localStorage.key(i);
                    data[key] = window.localStorage.getItem(key);
                }
                return data;
            """)

            all_sessions = []
            if os.path.exists(localstorage_path):
                with open(localstorage_path, "r") as file:
                    all_sessions = json.load(file)

            session_index = next((index for index, entry in enumerate(all_sessions) if entry["id"] == session_id), -1)
            if session_index != -1:
                all_sessions[session_index]["data"]["localStorage"] = local_storage_data
            else:
                all_sessions.append({
                    "id": session_id,
                    "data": {
                        "localStorage": local_storage_data,
                    }
                })

            with open(localstorage_path, "w") as file:
                json.dump(all_sessions, file, indent=2)

            print(f'Session with id "{session_id}" has been saved.')
        except Exception as e:
            print(f"Error saving localstorage.json: {e}")

    def run_get_session(self):
        self.open_url("https://web.telegram.org/a")

        WebDriverWait(self.browser, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//button[text()='Log in by phone Number']"))
        )
        self.browser.find_element(By.XPATH, "//button[text()='Log in by phone Number']").click()
        WebDriverWait(self.browser, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//label[@for='sign-in-phone-number']"))
        )
        label = self.browser.find_element(By.XPATH, "//label[@for='sign-in-phone-number']")
        label_text = label.text
        print(label_text)
        input_element = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="sign-in-phone-number"]'))
        )
        value = self.ask_question("Masukan Nomber: ")

        input_element.send_keys(value)
        WebDriverWait(self.browser, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//button[@type='submit' and contains(@class, 'Button default primary has-ripple')]"))
        )
        self.browser.find_element(By.XPATH, "//button[@type='submit' and contains(@class, 'Button default primary has-ripple')]").click()
        WebDriverWait(self.browser, 30).until(
            EC.visibility_of_element_located((By.XPATH, "//p[@class='note']"))
        )
        note_element = self.browser.find_element(By.XPATH, "//p[@class='note']")
        note_text = note_element.text
        print(note_text)

        input_otp = WebDriverWait(self.browser, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="sign-in-code"]'))
        )
        value = self.ask_question("Masukan code otp: ")

        input_otp.send_keys(value)
        input_otp.click()
        answer = self.ask_question("Sudah login? (y/n): ")
        session_id = self.ask_question("Enter session ID: ")

        if answer.lower() == "y":
            self.save_local_storage(session_id)
        else:
            if self.load_local_storage(session_id):
                self.browser.refresh()
                print("Login otomatis menggunakan localStorage berhasil.")
                self.delay(5)
        self.close()  # Use inherited close method to quit browser
        print("Browser closed.")