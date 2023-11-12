import json
from datetime import date
from enum import Enum

import requests


class Area(Enum):
    SMT_IN = "SMT_IN"
    SMT_OUT = "SMT_OUT"
    PACKING = "PACKING"


class Type(Enum):
    INFO_SUMMARY_HOUR = 'INFO_SUMMARY_HOUR'
    MISS_TARGET = 'MISS_TARGET'


class Host(Enum):
    LOCAL = 'http://10.13.56.65:3040'
    REMOTE = 'http://10.13.33.46:3040'


def get_ip(host: Host):
    match host:
        case Host.LOCAL:
            return host.value
        case Host.REMOTE:
            return host.value


def get_credentials():
    return {
        'user': 'iradi_admin',
        'password': 'root2000'
    }


def logs_dir():
    return f'{get_ip(Host.LOCAL)}/api/collections/logs/records'


def get_token():
    try:
        url = f'{get_ip(Host.LOCAL)}/api/collections/users/auth-with-password'
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


def post_target_loss_log(index, line, uph, target):
    current_day = date.today().strftime("%Y-%m-%d")
    try:
        logs = requests.post(
            url=logs_dir(),
            headers={
                'Content-Type': 'application/json',
                'Authorization': get_token()
            },
            data=json.dumps({
                "date": current_day,
                "hour": "00:00:00",
                "index": index,
                "line": line,
                "area": Area.PACKING.value,
                "type": Type.MISS_TARGET.value,
                "payload": {
                    "fix_val": [
                        index,
                        uph,
                        target
                    ]
                }
            })
        )

        print(logs.status_code)
        return logs.status_code

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
