import requests
import time
import json
import os
from random import randint
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
from base.getInitData import initData
from base.browser import Browser
import sys

class notPixels(Browser):
    def __init__(self, browser_instance):
        super().__init__(browser_instance)  # Properly initialize the parent class
        self.initData_instance = initData(self.browser)  # Use self.browser from the parent class
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def user_agent_generator():
        windows_nt_version = randint(7, 99)
        chrome_version = randint(96, 196)
        webkit_version = randint(500, 1200)
        os_platform = f"Windows NT {windows_nt_version}.0; Win64; x64"
        user_agent = (f"Mozilla/5.0 ({os_platform}) AppleWebKit/{webkit_version}.36 "
                      f"(KHTML, like Gecko) Chrome/{chrome_version}.0.3163.100 Safari/{webkit_version}.36")
        return user_agent

    @staticmethod
    def sleep(seconds):
        time.sleep(seconds)


    def resource_path(self, relative_path):
        """ Get the absolute path to the resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def load_init_data(self):
        query_data_path = self.resource_path("data/initData/init_data.json")
        if os.path.exists(query_data_path):
            with open(query_data_path, "r") as file:
                return json.load(file)
        else:
            print("bearer_data.json not found.")
            return []

    def get_user(self, init_data, random_user_agent, session_id):
        try:
            response = requests.get("https://notpx.app/api/v1/users/me", headers={
                "accept": "application/json, text/plain, */*",
                "authorization": f"initData {init_data}",
                "User-Agent": random_user_agent
            }, timeout=50)
            cek = response.json()
            if cek.get('code') == 6:
                self.logger.warning(f"Unauthorized access for session_id: {session_id}. Refreshing initData...")
                refreshed_data = self.initData_instance.run_get_initData(url="https://web.telegram.org/a/#7249432100", session_id=session_id)
                if refreshed_data:
                    self.logger.info("Successfully refreshed initData.")
                    return refreshed_data
                else:
                    self.logger.error("Failed to refresh initData.")
                    return None
            return response.json()

        except Exception as e:
            self.logger.error("Error in getting user info: %s", e)
            return None

    def get_user_info(self, init_data, random_user_agent):
        try:
            response = requests.get("https://notpx.app/api/v1/mining/status", headers={
                "accept": "application/json, text/plain, */*",
                "authorization": f"initData {init_data}",
                "User-Agent": random_user_agent
            }, timeout=50)
            return response.json()
        except Exception as e:
            print("Error in performing color change:", e)
            return None

    @staticmethod
    def get_random_pixel_id(min_id, max_id):
        return randint(min_id, max_id)

    def perform_action(self, init_data, pixel_id, new_color, random_user_agent):
        try:
            response = requests.post(
                "https://notpx.app/api/v1/repaint/start",
                json={"pixelId": pixel_id, "newColor": new_color},
                headers={
                    "accept": "application/json, text/plain, */*",
                    "authorization": f"initData {init_data}",
                    "content-type": "application/json",
                    "User-Agent": random_user_agent
                }, timeout=50
            )
            return response
        except Exception as e:
            print("Error in performing color change:", e)
            return None

    def mainNotPixels(self):
        random_user_agent = self.user_agent_generator()
        init_data_entries = self.load_init_data()
        
        if not init_data_entries:
            print("No valid initData found. Please run initdata.py first.")
            return

        while True:
            current_index = 0
            while current_index < len(init_data_entries):
                entry = init_data_entries[current_index]
                id = entry['id']
                init_data = entry['data']

                print(f"Processing initData entry: {id}")

                user = self.get_user(init_data, random_user_agent, id)
                try:
                    user_id = user.get("id")
                    user_name = user.get("firstName")
                    user_repaint = user.get("repaints")
                    user_balance = user.get("balance")
                    user_ref = user.get("friends")

                    print("id : ", user_id)
                    print("Name : ", user_name)
                    print("Total Repaint : ", user_repaint)
                    print("Balance : ", user_balance)
                    print("User Ref : ", user_ref)
                except AttributeError as e:
                    print("Error accessing user data:", e)
                    print("Continuing to next entry...")
                    current_index += 1
                    continue
                
                user_info = self.get_user_info(init_data, random_user_agent)
                if not user_info:
                    print("Failed to retrieve user info. Moving to the next initData entry.")
                    current_index += 1
                    continue
                charges = user_info.get("charges")

                while charges > 0:
                    try:
                        pixel_id = self.get_random_pixel_id(4002, 366308)
                        new_color = "#e46e6e"
                        self.perform_action(init_data, pixel_id, new_color, random_user_agent)
                        user_info = self.get_user_info(init_data, random_user_agent)
                        if not user_info:
                            print("Failed to retrieve updated user info.")
                            break

                        charges = user_info.get("charges")
                        print(f"Remaining Charges: {charges}")
                    except Exception as e:
                        print("Error during repaint action:", e)

                print(f"All charges used for {id}. Switching to next entry.")
                current_index += 1

            print("All initData entries have been processed. Sleeping for 10 minutes.")
            time.sleep(100)
