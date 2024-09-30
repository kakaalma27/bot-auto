import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def get_current_timestamp():
    return int(time.time())

def is_session_expired(session):
    current_time = get_current_timestamp()
    return session['expiry'] < current_time

def check_sessions():
    if not os.path.exists("D:\\STILL-WORK\\data\\authLogin\\localstorage.json"):
        print("localstorage.json not found.")
        return

    with open("D:\\STILL-WORK\\data\\authLogin\\localstorage.json", "r") as file:
        all_sessions = json.load(file)

    if not isinstance(all_sessions, list):
        print("Invalid session format.")
        return

    for session in all_sessions:
        if is_session_expired(session):
            print(f'Session ID "{session["id"]}" has expired.')
        else:
            print(f'Session ID "{session["id"]}" is still valid.')

driver = webdriver.Chrome()
if __name__ == "__main__":
    check_sessions()
