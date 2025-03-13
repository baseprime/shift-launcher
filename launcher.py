import os
import json
import requests
import webview
import configparser
from threading import Thread

CONFIG_FILE = os.path.join(os.getenv('APPDATA', 'C:\ShiftOS'), 'launcher_settings.ini')
API_URL = 'http://192.168.86.34:8000'
TOKEN = None

# Load or create config
def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        config['Settings'] = {'api_url': API_URL, 'steam_id': ''}
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
    config.read(CONFIG_FILE)
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def authenticate(username, password):
    global TOKEN
    response = requests.post(f'{API_URL}/auth/token', json={'username': username, 'password': password})
    if response.status_code == 200:
        TOKEN = response.json().get('access')
        return True
    return False

def fetch_data(endpoint):
    headers = {'Authorization': f'Bearer {TOKEN}'} if TOKEN else {}
    response = requests.get(f'{API_URL}/{endpoint}', headers=headers)
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def download_race_file(uuid):
    headers = {'Authorization': f'Bearer {TOKEN}'}
    response = requests.get(f'{API_URL}/calendars/{uuid}/race.ini', headers=headers, stream=True)
    if response.status_code == 200:
        file_path = os.path.join(os.getenv('APPDATA', 'C:\ShiftOS'), 'race.ini')
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        os.startfile('acs.exe')

def start_ui():
    webview.create_window('Shift Launcher', 'launcher.html', fullscreen=True)
    webview.start()

if __name__ == '__main__':
    config = load_config()
    API_URL = config['Settings']['api_url']
    
    # Start the UI in a separate thread
    Thread(target=start_ui).start()
