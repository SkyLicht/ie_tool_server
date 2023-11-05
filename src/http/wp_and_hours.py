import requests

from src.http.get_data_from_mackenzie_api import get_outputs_current_day


def get_wp_and_hours():
    def find_hours_in_line(data, line):
        for hours in data:
            if line == hours['line']:
                return hours["hours"]
        return {"hours": []}

    outputs = get_outputs_current_day()
    wp_plan = get_wp_and_output()
    fix_data = {
        "lines": []
    }
    # clean the data
    for wps in wp_plan:
        # print(wps)
        temp_uph_d = 0
        if len((wps['expand']['uph'])) > 0:
            temp_uph_d = wps['expand']['uph'][0]['qty']

        hours_line = find_hours_in_line(outputs, wps['line'])

        fix_data.get('lines').append(
            {
                'line': wps['line'],
                'target_oee': wps['eff'],
                'uhp_d': temp_uph_d,
                'uhp_i': wps['uphi'],  # wps['eff'] * temp_uph_d if wps['eff'] > 0 else 0,
                'hours': hours_line
            }
        )

    return fix_data


def get_wp_and_output():
    from datetime import date
    current_day = date.today().strftime("%Y-%m-%d")
    #2023-11-03
    work_plan = requests.get(
        url=f'http://10.13.33.46:3030/api/collections/workplan/records?filter=(work_date ~ "2023-11-03")&expand=uph',
        headers={
            'Content-Type': 'application/json',
            'Authorization': ''
        }

    )
    if len(work_plan.json()["items"]) > 0:
        return work_plan.json()["items"]

    return []
