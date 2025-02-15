import os
from dotenv import load_dotenv
import requests
import time
import subprocess
import json

load_dotenv()

APP_KEY = os.getenv("APPLICATION_API_KEY")
CLIENT_KEY = os.getenv("CLIENT_API_KEY")
PANEL_URL = os.getenv("PANEL_URL")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_SECONDS", 300))
PURGE_THRESHOLD = int(os.getenv("PURGE_THRESHOLD_SECONDS", 604800))
EXCEPTED_SERVERS = os.getenv("EXCEPTED_SERVERS", "").split(',')

def get_all_servers():
    headers = {'Authorization': f'Bearer {APP_KEY}', 'Accept': 'application/json'}
    response = requests.get(f'{PANEL_URL}/api/application/servers', headers=headers)
    servers = response.json()['data']
    return servers


def delete_server(container_name):
    server = next((server for server in all_servers if server['attributes']['uuid'] == container_name), None)
    if server:
        server_id = server['attributes']['id']
        server_name = server['attributes']['name']
        headers = {'Authorization': f'Bearer {CLIENT_KEY}'}
        response = requests.delete(f'{PANEL_URL}/api/client/servers/{server_id}', headers=headers)
        if response.status_code == 204:
            print(f"Successfully deleted server '{server_name}' (UUID: {container_name})")
        else:
            print(
                f"Failed to delete server '{server_name}' (UUID: {container_name}) - Status Code: {response.status_code}")
            try:
                error_details = response.json()
                print(f"Error details: {error_details}")
            except json.JSONDecodeError:
                print("No JSON response, raw response:", response.text)
    else:
        print(f"Server with UUID {container_name} not found.")


def get_exited_containers():
    result = subprocess.run("docker inspect $(docker ps -aq -f status=exited)", shell=True, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Failed to parse Docker inspect output")
        return []


def parse_running_for(state):
    if 'FinishedAt' in state and state['FinishedAt'] != "":
        finished_time = state['FinishedAt']
        return int(time.time() - time.mktime(time.strptime(finished_time.split('.')[0], '%Y-%m-%dT%H:%M:%S')))
    return 0


while True:
    print(f"Check Interval: {CHECK_INTERVAL} seconds")
    print(f"Purge Threshold: {PURGE_THRESHOLD} seconds")
    print("Checking servers...")
    all_servers = get_all_servers()

    for container in get_exited_containers():
        container_name = container.get("Name", "").strip('/')
        running_for = parse_running_for(container.get("State", {}))
        print(f"Container {container_name}: Offline for {running_for} seconds")

        if container_name in EXCEPTED_SERVERS:
            print(f"Server {container_name} is excepted from deletion. Skipping...")
            continue

        if container_name in [server['attributes']['uuid'] for server in all_servers] and running_for > PURGE_THRESHOLD:
            print(f"Server {container_name} exceeded threshold. Deleting...")
            delete_server(container_name)
    time.sleep(CHECK_INTERVAL)
