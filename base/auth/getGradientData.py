import json
import time
import os
import sys
import random
import requests
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from base.browser import Browser
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from concurrent.futures import ThreadPoolExecutor, as_completed

class tGradient(Browser):
    def __init__(self, browser_instance):
        super().__init__(browser_instance)

    def ask_question(self, query):
        return input(query)

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def load_active_proxies(self):
        try:
            with open('data/activ_proxies.txt', 'r') as file:
                proxies = [line.strip() for line in file if line.strip()]
                if proxies:
                    return proxies
                else:
                    print("No proxies available in the file.")
                    return None
        except FileNotFoundError:
            print("Active proxy file not found!")
            return None

    def run_browser_with_proxy(self, proxy):
        print(f"Using proxy: {proxy}")

        proxy_browser = Browser(proxy=proxy, extension="data/undefined 1.0.6.0.crx")
        browser = proxy_browser.browser  
        self.open_url("https://app.gradient.network/")
        time.sleep(5)

        handles = browser.window_handles
        browser.switch_to.window(handles[0])
        time.sleep(2)

        browser.switch_to.window(handles[1])
        time.sleep(2)
        
        try:
            WebDriverWait(browser, 30).until(
                EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/div/div/div[2]/div[1]/input"))
            )
        except TimeoutException:
            print(f"Element not found using proxy: {proxy}, refreshing the page...")
            time.sleep(10)
            browser.refresh()
            try:
                WebDriverWait(browser, 30).until(
                    EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/div/div/div[2]/div[1]/input"))
                )
            except TimeoutException:
                print(f"Element still not found after refresh with proxy: {proxy}. Exiting.")
                return  # Skip to next proxy if this one fails

        # Continue with the login process
        email = browser.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/div/div[2]/div[1]/input")
        email.click()
        email.send_keys("kakaalma369@gmail.com")
        time.sleep(0.5)

        WebDriverWait(browser, 30).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/div/div/div[2]/div[2]/span/input"))
        )
        password = browser.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/div/div[2]/div[2]/span/input")
        password.click()
        password.send_keys("Batalkan86@")
        time.sleep(0.5)

        WebDriverWait(browser, 30).until(
            EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[2]/div/div/div/div[4]/button[1]"))
        )
        submit = browser.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/div/div[4]/button[1]")
        submit.click()
        time.sleep(10)

        browser.execute_script("window.open('https://www.google.com', '_blank');")

        new_tab_handle = browser.window_handles[-1]
        browser.switch_to.window(new_tab_handle)

        while True:
            browser.refresh()
            time.sleep(3)

    def run_get_Gradient(self):
        proxies = self.load_active_proxies()

        if not proxies:
            print("No active proxies available. Exiting.")
            return

        with ThreadPoolExecutor(max_workers=len(proxies)) as executor:
            futures = [executor.submit(self.run_browser_with_proxy, proxy) for proxy in proxies]

            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"An error occurred: {e}")