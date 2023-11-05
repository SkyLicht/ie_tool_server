import json
from datetime import date

import requests


def get_ip():
    return 'http://127.0.0.1:8090'
    pass


def get_credentials():
    return {
        'user': 'iradi_admin',
        'password': 'root2000'
    }


def logs_dir():
    return f'{get_ip()}/api/collections/logs/records'
    pass


def get_token():
    try:
        url = f'{get_ip()}/api/collections/users/auth-with-password'
        token = requests.post(
            url=url,
            data={"identity": get_credentials()['user'], "password": get_credentials()['password']}
        )

        if token.status_code == 200:
            return token.json()['token']

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    return ''


def get_current_day_lost_target_logs():
    current_day = date.today().strftime("%Y-%m-%d")
    try:
        logs = requests.get(
            url=logs_dir() + f'?perPage=500&filter=(date = "{current_day}" %26%26 type = "MISS_TARGET")',
            headers={
                'Content-Type': 'application/json',
                'Authorization': get_token()
            }
        )

        if logs.status_code == 200:
            return logs.json()['items']
            pass

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)

