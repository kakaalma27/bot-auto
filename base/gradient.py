import requests
import time
import json
import os
from random import randint
import random

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging
from base.auth.getGradientData import tGradient
from base.browser import Browser
import sys

class gradient(Browser):
    def __init__(self, browser_instance):
        super().__init__(browser_instance)
        self.tDataGradient_instance = tGradient(self.browser) 
        self.query_data_entries = self.load_init_data()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    @staticmethod
    def user_agent_generator():
        windows_nt_version = random.randint(7, 99)
        chrome_version = random.randint(96, 196)
        webkit_version = random.randint(500, 1200)
        os_platform = f"Windows NT {windows_nt_version}.0; Win64; x64"
        user_agent = (f"Mozilla/5.0 ({os_platform}) AppleWebKit/{webkit_version}.36 "
                      f"(KHTML, like Gecko) Chrome/{chrome_version}.0.3163.100 Safari/{webkit_version}.36")
        return user_agent

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_init_data(self):
        query_data_path = self.resource_path("data/gradient/gradient_data.json")
        if os.path.exists(query_data_path):
            with open(query_data_path, "r") as file:
                return json.load(file)
        else:
            self.logger.error("gradient_data.json not found.")
            return []


    def get_proxy(self):
        if self.proxy_list:
            for proxy in self.proxy_list:
                if self.check_proxy(proxy):
                    return proxy
        return None

    def get_user(self, query_data, random_user_agent, session_id):
        try:
            response = requests.post(
                "https://api.gradient.network/api/user/profile",
                headers={
                    "accept": "application/json, text/plain, */*",
                    "authorization": f"Bearer {query_data}",
                    "User-Agent": random_user_agent
                },
                timeout=100
            )
            if response.status_code == 403:
                self.logger.warning(f"Unauthorized access for session_id: {session_id}. Refreshing initData...")
                refreshed_data = self.tDataGradient_instance.run_get_Gradient(url="https://app.gradient.network/")
                if refreshed_data:
                    self.logger.info("Successfully refreshed initData.")
                    return refreshed_data
                else:
                    self.logger.error("Failed to refresh initData.")
                    return None

            if response.status_code == 200 and response.text:
                cek = response.json()
                return cek
            else:
                self.logger.error(f"Invalid or empty response for session_id: {session_id}")
                return None
        except Exception as e:
            self.logger.error(f"Error in getting user info: {e}")
            return None
    def mainBotGradient(self):
        random_user_agent = self.user_agent_generator()

        while True:
            current_index = 0 
            entries = self.load_init_data()
            
            while current_index < len(entries):
                entry = entries[current_index]
                session_id = entry['id']
                query_data = entry['data']['localStorage']
                user = self.get_user(query_data, random_user_agent, session_id)
                email = user['data']['email']
                balance = user['data']['point']['balance']
                print("Running Gradient...")
                print(f"Email: {email}, Balance: {balance}")
                self.open_url("https://www.google.com/")
                current_index += 1
            time.sleep(50)

