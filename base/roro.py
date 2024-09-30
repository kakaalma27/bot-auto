import os
import json
import time
import requests
from random import randint
from base.getQuery import Query
from base.browser import Browser
from selenium import webdriver
import sys

class Kuroro(Browser):
    def __init__(self, browser_instance):
        super().__init__(browser_instance)
        self.bearer_instance = Query(browser_instance)
        self.query_data_entries = self.load_query_data()
        self.random_user_agent = self.user_agent_generator()
        self.coordinate_share = [{"x": 135, "y": 412}]
        self.coordinate_feed = [{"x": 206, "y": 208}]

    def user_agent_generator(self):
        windows_nt_version = randint(7, 99)
        chrome_version = randint(96, 196)
        webkit_version = randint(500, 1200)
        os_platform = f"Windows NT {windows_nt_version}.0; Win64; x64"
        user_agent = (f"Mozilla/5.0 ({os_platform}) AppleWebKit/{webkit_version}.36 "
                      f"(KHTML, like Gecko) Chrome/{chrome_version}.0.3163.100 Safari/{webkit_version}.36")
        return user_agent

    def resource_path(self, relative_path):
        """ Get the absolute path to the resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def load_query_data(self):
        query_data_path = self.resource_path("data/bearer/bearer_data.json")
        if os.path.exists(query_data_path):
            with open(query_data_path, "r") as file:
                return json.load(file)
        else:
            print("bearer_data.json not found.")
            return []

    def get_user(self, query_data, session_id):
        try:
            response = requests.get(
                "https://ranch-api.kuroro.com/api/Game/GetPlayerState",
                headers={
                    "accept": "application/json, text/plain, */*",
                    "authorization": f"Bearer {query_data}",
                    "User-Agent": self.random_user_agent,
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site",
                    "Referer": "https://ranch.kuroro.com/",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                }, timeout=50
            )

            if response.status_code == 401:
                print(f"Unauthorized access for session_id: {session_id}. Refreshing queryData...")
                refreshed_data = self.bearer_instance.run_get_Bearer(url="https://web.telegram.org/a/#7263554914", session_id=session_id)
                if refreshed_data:
                    print("Successfully refreshed bearer.")
                    return refreshed_data
                else:
                    print("Failed to refresh bearer.")
                    return None

            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as err:
            print(f"An HTTP error occurred: {err}")
            return None

        except Exception as err:
            print(f"An error occurred: {err}")
            return None

    def save_coordinates(self, query_data, coordinates):
        try:
            response = requests.post(
                "https://ranch-api.kuroro.com/api/Bf/Save",
                json=coordinates,
                headers={
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "en-US,en;q=0.9",
                    "authorization": f"Bearer {query_data}",
                    "priority": "u=1, i",
                    "User-Agent": self.random_user_agent,
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site",
                    "Referer": "https://ranch.kuroro.com/",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                }, timeout=50
            )
            return response
        except Exception as e:
            print("Error in saving coordinates:", e)
            return None

    def perform_action(self, query_data, feed_amount, mine_amount):
        try:
            response = requests.post(
                "https://ranch-api.kuroro.com/api/Clicks/MiningAndFeeding",
                json={
                    "feedAmount": feed_amount,
                    "mineAmount": mine_amount,
                },
                headers={
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "en-US,en;q=0.9",
                    "authorization": f"Bearer {query_data}",
                    "priority": "u=1, i",
                    "User-Agent": self.random_user_agent,
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site",
                    "Referer": "https://ranch.kuroro.com/",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                }, timeout=50
            )
            return response
        except Exception as e:
            print("Error in performing action:", e)
            return None

    def purpose_upgrade(self, query_data):
        try:
            response = requests.get(
                "https://ranch-api.kuroro.com/api/Upgrades/GetPurchasableUpgrades",
                headers={
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "en-US,en;q=0.9",
                    "authorization": f"Bearer {query_data}",
                    "priority": "u=1, i",
                    "User-Agent": self.random_user_agent,
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site",
                    "Referer": "https://ranch.kuroro.com/",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                }, timeout=50
            )
            return response.json()
        except Exception as e:
            print("Error in getting upgrades:", e)
            return None

    def update(self, query_data, upgrade_id, max_retries=3):
        payload = {"upgradeId": upgrade_id}
        print("Payload being sent:", payload)

        for attempt in range(max_retries):
            try:
                response = requests.post(
                    "https://ranch-api.kuroro.com/api/Upgrades/BuyUpgrade",
                    json=payload,
                    headers={
                        "accept": "application/json, text/plain, */*",
                        "authorization": f"Bearer {query_data}",
                        "User-Agent": self.random_user_agent,
                    }, timeout=50
                )

                if 'application/json' in response.headers.get('Content-Type', ''):
                    return response.json()
                else:
                    print("Non-JSON response received.")
                    return None

            except Exception as e:
                print(f"Error in purchasing upgrade (attempt {attempt + 1}):", e)

            if response.status_code == 500 and attempt < max_retries - 1:
                print("Server error, retrying...")
                continue 

        return None

    def boosters(self, query_data):
        try:
            response = requests.post(
                "https://ranch-api.kuroro.com/api/CoinsShop/BuyItem",
                json={"itemId": "raffle-ticket"},
                headers={
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "en-US,en;q=0.9",
                    "authorization": f"Bearer {query_data}",
                    "priority": "u=1, i",
                    "User-Agent": self.random_user_agent,
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site",
                    "Referer": "https://ranch.kuroro.com/",
                    "Referrer-Policy": "strict-origin-when-cross-origin",
                }, timeout=50
            )
            return response.json()
        except Exception as e:
            print("Error in buying raffle ticket:", e)
            return None

    def mainKuroro(self):
        if not self.query_data_entries:
            print("No valid queryData found. Please run querydata.py first.")
            return

        while True:
            current_index = 0  # Reset index for a new iteration
            while current_index < len(self.query_data_entries):
                entry = self.query_data_entries[current_index]
                session_id = entry['id']
                query_data = entry['data']

                try:
                    print(f"Processing bearer entry: {session_id}")
                    user = self.get_user(query_data, session_id)
                    if user is None:
                        print("Failed to retrieve user data. Moving to the next entry...")
                        current_index += 1
                        continue

                    energy_snapshot = user.get("energySnapshot")
                    if energy_snapshot:
                        energy_value = energy_snapshot.get("value")
                        print("Energy:", energy_value)

                    shards = user.get("shards")
                    print("Shards:", shards)
                except Exception as e:
                    print("Error during repaint action:", e)

                try:
                    while energy_value > 0:
                        try:
                            user = self.get_user(query_data, session_id)
                            if user is None:
                                print("Failed to retrieve updated user info.")
                                break

                            energy_snapshot = user.get("energySnapshot")
                            if energy_snapshot:
                                energy_value = energy_snapshot.get("value")
                                self.save_coordinates(query_data, self.coordinate_share)
                                self.perform_action(query_data, 0, 1)
                                print(f"Sisa Energy: {energy_value}")

                            if energy_value <= 0:
                                print("Energy is depleted. Exiting energy action loop.")
                                break

                        except Exception as e:
                            print("Error during action execution:", e)
                            break

                except Exception as e:
                    print("Error in the energy loop:", e)

                # Other actions can be added here
                time.sleep(100)  # Adding a delay to prevent rapid requests

                current_index += 1


