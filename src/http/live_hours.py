import json

import requests
from datetime import datetime
from typing import List
from src.http.get_data_from_mackenzie_api import LineWithOutputs, OutputsData
from src.lib.util import Server
from src.lib.util_config import get_ip


def live_dir(more: str = ''):
    return f'http://{get_ip(Server.ONLINE)}:3010/api/collections/line_live/records' + more


def clean_live_db():
    data = [
        'J01',
        'J02',
        'J03',
        'J05',
        'J06',
        'J07',
        'J08',
        'J09',
        'J10',
        'J11',
        'J12',
        'J13'
    ]
    if len(data) > 0:
        for line in data:
            for hour in range(0, 24):
                live_update_by_hour(
                    line=line,
                    data=OutputsData(
                        index=hour,
                        smt_in=0,
                        smt_out=0,
                        packing =0
                    )
                )


def live_update_hour(data: List[LineWithOutputs]):
    if len(data) > 0:
        current_hours = datetime.now().hour
        for element in data:
            hour_data = element.get_hour_by_index(current_hours)
            live_update_by_hour(line=element.line, data=hour_data)
    pass


def live_update_day(data: List[LineWithOutputs]):
    if len(data) > 0:
        for element in data:
            for hour_data in element.data:
                live_update_by_hour(line=element.line, data=hour_data)

    pass


def live_update_by_hour(line: str, data: OutputsData):
    try:
        livedata = requests.get(live_dir(f"?filter=(line = '{line}' %26%26 place = '{data.index}')"))
        print(f'data to update {data} ->', livedata.status_code)
        line_hour_id = livedata.json()['items'][0]['id']

        live_patch_hour_by_id(
            hour_id=line_hour_id,
            smt_in=data.smt_in,
            smt_out=data.smt_out,
            packing=data.packing)

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)

    pass


def live_patch_hour_by_id(hour_id: str, smt_in: int, smt_out: int, packing: int):
    try:
        patch = (requests.patch(
            url=live_dir(f'/{hour_id}'),
            headers={
                'Content-Type': 'application/json',
            },
            data=json.dumps({
                "smt_in": smt_in,
                "smt_out": smt_out,
                "output": packing
            }))
        )

        print(f'hour {hour_id} updated, status -> {patch.status_code}')

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)
    pass
