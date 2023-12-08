import json

import requests
import datetime
from src.http.get_data_from_mackenzie_api import LineWithOutputs, OutputsData
from src.lib.util import Server
from src.lib.util_config import get_ip
from typing import List


def live_day_dir(more: str = ''):
    return f'http://{get_ip(Server.ONLINE)}:3030/api/collections/day/records' + more


def live_hour_dir(more: str = ''):
    return f'http://{get_ip(Server.ONLINE)}:3030/api/collections/hour/records' + more


def day_and_hours_update():
    pass


def post_day_and_hours_day_before(data: List[LineWithOutputs]):
    today = datetime.date.today()
    day = datetime.timedelta(days=1)
    yesterday = today - day

    print(yesterday.strftime("%Y-%m-%d"))
    exist = is_day_exist(yesterday.strftime("%Y-%m-%d"))
    if exist: return
    print('hello')

    for element in data:
        ids = []
        for hour in element.data:
            #print(f'line -> {element.line} | hour data -> {hour}')
            ids.append(post_hour(hour))
        post_day(ids, element.line, yesterday.strftime("%Y-%m-%d"))


def is_day_exist(date: str) -> bool:
    try:
        get_day = requests.get(
            url=live_day_dir(f'?filter=(work_date ~ "{date}")')
        )

        if get_day.status_code != 200: return False

        if len(get_day.json()['items']) > 0:
            return True
        else:
            return False

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)


def post_day(ids: List[str], line: str, date: str):
    try:
        post = requests.post(
            url='http://10.13.33.46:3030/api/collections/day/records',
            headers={
                'Content-Type': 'application/json'
            },
            data=json.dumps(
                {"work_date": date, "line": line, "hours": ids}
            )
        )
        print(f'post day line:{line} date:{date}. status -> {post.status_code}')
        pass
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    pass


def post_hour(hour: OutputsData) -> str:
    try:
        post_hours = requests.post(
            url='http://10.13.33.46:3030/api/collections/hour/records',
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTgxNTE3NDMsImlkIjoiang1cXc2eW5mM2QxY3o0IiwidHlwZSI6ImFkbWluIn0.aA73pdcN5g5hrgAF8tO4IZ3-YsLWYcAAnzRLB75PqAs'
            },
            data=json.dumps(
                {"place": hour.index, "smtIn": hour.smt_in, "smtOut": hour.smt_out, "packing": hour.packing}
            )
        )

        print(f'posst hour {hour} .status -> ', post_hours.status_code)
        return post_hours.json()['id']
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
