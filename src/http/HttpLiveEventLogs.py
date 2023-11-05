import json

import requests

from src.http.get_data_from_mackenzie_api import get_outputs_current_day


class HttpLiveEventsLogs:
    def __int__(self):
        pass

    def execute(self):
        wp_and_hours = self.get_wp_and_hours()
        print(wp_and_hours)
        get_lost_hours(wp_and_hours)

    def get_wp_and_hours(self):
        def find_hours_in_line(data, line):
            for hours in data:
                if line == hours['line']:
                    return hours["hours"]
            return {"hours": []}

        outputs = get_outputs_current_day()
        wp_plan = self.get_wp_and_output()
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
        print(fix_data)
        return fix_data

    def get_wp_and_output(self):
        from datetime import date
        current_day = date.today().strftime("%Y-%m-%d")
        work_plan = requests.get(
            url=f'http://10.13.33.46:3030/api/collections/workplan/records?filter=(work_date ~ "{current_day}")&expand=uph',
            headers={
                'Content-Type': 'application/json',
                'Authorization': ''
            }

        )

        if len(work_plan.json()["items"]) > 0:
            return work_plan.json()["items"]

        return []


def get_lost_hours(data):
    import datetime
    current_hour_index = datetime.datetime.now().hour

    lost_hour = []
    for element in data['lines']:
        target_oee = element['target_oee']
        uhp_d = element['uhp_d']
        uph_target = element['uhp_i']

        # wps['eff'] * temp_uph_d if wps['eff'] > 0 else 0
        target_lost = {
            "smt_in": [],
            "smt_out": [],
            "packing": []
        }
        for hour in element['hours']:
            if hour['index'] < current_hour_index:
                if hour['smt_in'] < uph_target:
                    target_lost['smt_in'].append({"index": hour['index'],
                                                  "uph": hour['smt_in'],
                                                  "target": uph_target
                                                  })

                if hour['smt_out'] < uph_target:
                    target_lost['smt_out'].append({"index": hour['index'],
                                                   "uph": hour['smt_out'],
                                                   "target": uph_target
                                                   })

                if hour['packing'] < uph_target:
                    target_lost['packing'].append({"index": hour['index'],
                                                   "uph": hour['packing'],
                                                   "target": uph_target
                                                   })
        lost_hour.append({
            "line": element['line'],
            "hours_lost": target_lost
        })

    print(json.dumps(lost_hour, indent=4))
