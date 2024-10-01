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
                }, 
                timeout=50,
            )

            if response.status_code == 401:
                print(f"Unauthorized access for session_id: {session_id}. Refreshing queryData...")
                refreshed_data = self.bearer_instance.run_get_Bearer(url="https://web.telegram.org/a/#7263554914")
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
            current_index = 0 
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
                    print("Error during processing:", e)
                    current_index += 1  # Ensure to move to the next entry in case of error
                    continue
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
                    while shards > 0:
                        try:
                            user = self.get_user(query_data, session_id)
                            if user is None:
                                print("Failed to retrieve updated user info.")
                                break

                            shards = user.get("shards")
                            if shards:
                                self.save_coordinates(query_data, self.coordinate_feed)
                                self.perform_action(query_data, 1, 0)
                                print(f"Sisa Energy: {shards}")

                            if shards <= 0:
                                print("shards is depleted. Exiting energy action loop.")
                                break

                        except Exception as e:
                            print("Error during action execution:", e)
                            break
                except Exception as e:
                    print("Error in the energy loop:", e)
                try:
                    print("try Upgrades")

                    updated_user_info = self.get_user(query_data, session_id)
                    total_coins = round(updated_user_info['coinsSnapshot']['value'])
                    print("Total cost:", total_coins)

                    upgrade_skill = self.purpose_upgrade(query_data)
                    tolerance = total_coins * 0.9
                    matching_items = []

                    for item in upgrade_skill:
                        if item['canBePurchased']:
                            price_difference = abs(item['cost'] - total_coins)
                            if price_difference <= tolerance:
                                matching_items.append(item)

                    if matching_items:
                        first_matching_item = matching_items[0]
                        print(f"First Matching Item: Name: {first_matching_item['name']}, Cost: {first_matching_item['cost']}, upgradeId: {first_matching_item['upgradeId']}")

                        upgrade_id = first_matching_item['upgradeId']
                        result = self.update(query_data, upgrade_id)
                        print("Upgrades skill:", result['name'])
                    else:
                        print("No matching items found.")

                    tiket = self.boosters(query_data)
                    print(tiket['message'])
                except Exception as e:
                    print("Error during upgrade:", str(e))

                current_index += 1  

            print("All initData entries have been processed. Sleeping for 15 minutes.")
            time.sleep(500)
