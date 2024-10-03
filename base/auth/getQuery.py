import json
import time
import os
import sys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from base.browser import Browser

class Query(Browser):
    def __init__(self, browser_instance):
        super().__init__(browser_instance)

    def resource_path(self, relative_path):
        """ Get the absolute path to the resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS  # Used by PyInstaller to store temporary files
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def ask_question(self, query):
        return input(query)

    def load_local_storage(self, session_id):
        localstorage_path = self.resource_path("data/authLogin/localstorage.json")
        
        if os.path.exists(localstorage_path):
            print("File found.")
        else:
            print("File not found.")
            return False

        try:
            with open(localstorage_path, "r") as file:
                data = json.load(file)

            session = next((entry for entry in data if entry["id"] == session_id), None)

            if not session:
                print(f'Session with id "{session_id}" not found.')
                return False

            local_storage = session["data"]["localStorage"]
            for key, value in local_storage.items():
                # Use inherited browser instance to execute the script
                self.browser.execute_script(f"window.localStorage.setItem('{key}', '{value}');")
            
            return True
        except Exception as e:
            print(f"Error loading localstorage.json: {e}")
            return False

    def update_init_data(self, session_id, new_data):
        init_data_path = self.resource_path("data/bearer/bearer_data.json")

        if not os.path.exists(init_data_path):
            with open(init_data_path, "w") as file:
                json.dump([], file)
            print(f"File {init_data_path} created.")

        try:
            with open(init_data_path, "r") as file:
                data = json.load(file)

            for entry in data:
                if entry["id"] == session_id:
                    entry["data"] = new_data
                    break
            else:
                data.append({"id": session_id, "data": new_data})

            with open(init_data_path, "w") as file:
                json.dump(data, file, indent=4)

            print(f"Init data updated for session ID: {session_id}")
        except Exception as e:
            print(f"Error updating init data: {e}")

    def get_all_session_ids(self):
        """Load all session IDs from localstorage.json."""
        localstorage_path = self.resource_path("data/authLogin/localstorage.json")

        if not os.path.exists(localstorage_path):
            print("localstorage.json not found.")
            return []

        try:
            with open(localstorage_path, "r") as file:
                data = json.load(file)
                session_ids = [entry["id"] for entry in data]
                return session_ids
        except Exception as e:
            print(f"Error reading localstorage.json: {e}")
            return []

    def run_get_Bearer(self, url=""):
        if not url: 
            url = self.ask_question("Enter the URL:")

        session_ids = self.get_all_session_ids()
        if not session_ids:
            print("No session IDs found.")
            return

        max_retries = 3  # Define maximum retries for fetching initData

        for session_id in session_ids:
            print(f"Processing session ID: {session_id}")
            try:
                self.open_url("https://web.telegram.org/a")

                if self.load_local_storage(session_id):
                    self.browser.refresh()
                    print(f"Automatic login using localStorage for session ID {session_id} succeeded.")
                    time.sleep(5)

                self.browser.execute_script("window.open('');")
                self.browser.switch_to.window(self.browser.window_handles[1])
                print(f"Opening URL: {url}")
                self.browser.get(url)

                # Click the "start" button
                try:
                    WebDriverWait(self.browser, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "span.bot-menu-text"))
                    )
                    self.browser.find_element(By.CSS_SELECTOR, "span.bot-menu-text").click()
                    print('Clicked on the "start" button.')
                except Exception as e:
                    print(f"Error clicking start: {e}")

                # Click the "Confirm" button in the popup
                try:
                    WebDriverWait(self.browser, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "button.Button.confirm-dialog-button.default.primary.text"))
                    )
                    self.browser.find_element(By.CSS_SELECTOR, "button.Button.confirm-dialog-button.default.primary.text").click()
                    print('Clicked on the "Confirm" button in the popup.')
                except Exception as e:
                    print(f"Error clicking confirm")

                # Switch to iframe and fetch initData with retries
                retries = 0
                while retries < max_retries:
                    try:
                        WebDriverWait(self.browser, 10).until(
                            EC.visibility_of_element_located((By.CSS_SELECTOR, "iframe.OmY14FFl"))
                        )
                        frame = self.browser.find_element(By.CSS_SELECTOR, "iframe.OmY14FFl")
                        self.browser.switch_to.frame(frame)
                        time.sleep(5)

                        init_data = self.browser.execute_script("return window.Telegram.WebApp.initData;")
                        if init_data:
                            self.update_init_data(session_id, init_data)
                            print(f"Init data fetched and updated for session ID {session_id}.")
                            break  # Exit retry loop if successful
                        else:
                            raise Exception("Init data not available")
                    except Exception as e:
                        retries += 1
                        print(f"Attempt {retries} to fetch initData failed for session ID {session_id}: {e}")
                        if retries == max_retries:
                            print(f"Max retries reached for session ID {session_id}. Moving on.")
                        else:
                            time.sleep(3)  # Wait before retrying
            except Exception as e:
                print(f"An error occurred while processing session ID {session_id}: {e}")
            finally:
                if len(self.browser.window_handles) > 1:
                    self.browser.close()
                    self.browser.switch_to.window(self.browser.window_handles[0])

        self.close()
        print("All sessions processed. Browser closed.")

