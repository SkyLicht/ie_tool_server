import json

import requests
from enum import Enum

from src.http.get_data_from_mackenzie_api import get_outputs_current_day


class Host(Enum):
    LOCAL = 'http://10.13.56.65:3030'
    REMOTE = 'http://10.13.33.46:3030'


def wp_v2_url(host: Host):
    match host:
        case Host.LOCAL:
            return f'{host.value}/api/collections/workplanv2/records'
        case Host.REMOTE:
            return f'{host.value}/api/collections/workplanv2/records'


def get_wp_and_hours():  # add the wp and the mackenzie api data
    def find_hours_in_line(data, line):
        for hours in data:
            if line == hours['line']:
                return hours["hours"]
        return {"hours": []}

    outputs = get_outputs_current_day()  # mackenzie api data
    print('--------------------------------------------')
    print('mackenzie, ->', json.dumps(outputs, indent= 4))
    wp_plan = get_wp_current_day()
    fix_data = {
        "lines": []
    }
    # clean the data
    for wps in wp_plan:
        temp_uph_d = 0
        if wps['expand']['model'] is not None:
            temp_uph_d = wps['expand']['model']['uph']

        hours_line = find_hours_in_line(outputs, wps['line'])

        fix_data.get('lines').append(
            {
                'line': wps['line'],
                'target_oee': wps['target_oee'],
                'uhp_d': temp_uph_d,
                'uhp_i': wps['uph_i'],  # wps['eff'] * temp_uph_d if wps['eff'] > 0 else 0,
                'hours': hours_line
            }
        )
    return fix_data


def get_wp_current_day():
    from datetime import date
    current_day = date.today().strftime("%Y-%m-%d")
    try:
        work_plan = requests.get(
            url=f'{wp_v2_url(Host.LOCAL)}?filter=(work_date = "{current_day}")&expand=model',
            headers={
                'Content-Type': 'application/json',
                'Authorization': ''
            }
        )
        if len(work_plan.json()['items']) > 0:
            return work_plan.json()['items']

    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("OOps: Something Else", err)

    return []
