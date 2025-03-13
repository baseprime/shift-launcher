import os
import json
import requests
import webview
import configparser

CONFIG_FILE = "C:\\ShiftOS\\Launcher\\launcher_settings.ini"
API_URL = 'http://rivendell.local:8000'
TOKEN = None

# Load or create config
def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        config['Settings'] = {'api_url': API_URL, 'steam_id': '', 'fullscreen': 'true', 'token': ''}
        with open(CONFIG_FILE, 'w') as configfile:
            config.write(configfile)
    config.read(CONFIG_FILE)
    return config

def save_config(config):
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def authenticate(username, password):
    global TOKEN
    config = load_config()
    API_URL = config['Settings'].get('api_url', 'http://rivendell.local:8000')
    response = requests.post(f'{API_URL}/auth/token', json={'username': username, 'password': password})
    if response.status_code == 200:
        TOKEN = response.json().get('access')
        config['Settings']['token'] = TOKEN
        save_config(config)
        return True
    return False

def get_token():
    global TOKEN
    config = load_config()
    TOKEN = config['Settings'].get('token', '')
    return TOKEN

def fetch_data(endpoint):
    config = load_config()
    API_URL = config['Settings'].get('api_url', 'http://rivendell.local:8000')
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    response = requests.get(f'{API_URL}/{endpoint}', headers=headers)
    if response.status_code == 401:
        return 'UNAUTHORIZED'
    if response.status_code == 200:
        return response.json().get('results', [])
    return []

def download_race_file(uuid):
    config = load_config()
    API_URL = config['Settings'].get('api_url', 'http://rivendell.local:8000')
    token = get_token()
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{API_URL}/calendars/{uuid}/race.ini', headers=headers, stream=True)
    if response.status_code == 200:
        file_path = "C:\\ShiftOS\\Launcher\\race.ini"
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        os.startfile('acs.exe')

def check_auth_and_start():
    global TOKEN
    config = load_config()
    API_URL = config['Settings'].get('api_url', 'http://rivendell.local:8000')
    TOKEN = get_token()
    fullscreen = config['Settings'].get('fullscreen', 'true').lower() == 'true'

    # Expose Python functions to JavaScript
    js_api = {
        'load_config': load_config,
        'save_config': save_config,
        'authenticate': authenticate,
        'download_race_file': download_race_file,
    }

    print("Exposed API functions:", js_api)  # Debugging: Check the js_api object

    # Create the window with the js_api object
    window = webview.create_window(
        'Shift Launcher',
        f'file:///{os.path.abspath("C:/ShiftOS/Launcher/launcher.html")}',
        fullscreen=fullscreen,
        # js_api=js_api  # Pass the js_api object
    )

    window.expose(load_config)
    window.expose(save_config)
    window.expose(authenticate)
    window.expose(download_race_file)

    # Start the webview event loop
    webview.start(debug=True, gui='qt')

if __name__ == '__main__':
    check_auth_and_start()
