import itertools
import json
import asyncio
from datetime import datetime

from src.http.read_logs import get_current_day_lost_target_logs
from src.http.wp_and_hours import get_wp_and_hours


class TargetMissLogs:

    def __init__(self):
        print('init target miss logs')
        self.wp = get_wp_and_hours()
        self.logs = []
        self.LINES = ['J01', 'J02', 'J03', 'J05', 'J06', 'J07', 'J08', 'J09', 'J10', 'J11', 'J12', 'J13']

    def execute(self):
        print('execute target miss logs')
        # first step,load the miss target events
        self.post_lost_target()

        asyncio.get_event_loop().run_until_complete(self.start())
        asyncio.get_event_loop().run_until_complete(self.read())

    async def start(self):
        run = True
        while run:
            if datetime.now().second >= 58:
                run = False
            await asyncio.sleep(1)

    async def read(self):
        run = True
        await_time = 30
        count = -1
        update = False

        while run:
            print(count)

            if datetime.now().minute != count:
                print(datetime.now())
                update = True
                print("update")

            if update:
                if datetime.now().minute == 1:
                    print("it's 01")
                    print('db request')

            count = datetime.now().minute
            update = False
            await asyncio.sleep(await_time)

    def load_logs(self):
        logs = get_current_day_lost_target_logs()
        # classify logs by line
        temp_lines = []

        for line in self.LINES:
            temp_logs = []
            temp_smt_in_logs = []
            temp_smt_out_logs = []
            temp_packing_logs = []
            for log in logs:

                if log['line'] == line:

                    if log['area'] == 'SMT_IN':
                        temp_smt_in_logs.append(
                            {
                                'id': log['id'],
                                'line': line,
                                'date': log['date'],
                                'hour': log['hour'],
                                'index': log['index'],
                                'area': log['area'],
                                'type': log['type'],
                                'payload': log['payload']

                            })

                    if log['area'] == 'SMT_OUT':
                        temp_smt_out_logs.append(
                            {
                                'id': log['id'],
                                'line': line,
                                'date': log['date'],
                                'hour': log['hour'],
                                'index': log['index'],
                                'area': log['area'],
                                'type': log['type'],
                                'payload': log['payload']

                            })

                    if log['area'] == 'PACKING':
                        temp_packing_logs.append(
                            {
                                'id': log['id'],
                                'line': line,
                                'date': log['date'],
                                'hour': log['hour'],
                                'index': log['index'],
                                'area': log['area'],
                                'type': log['type'],
                                'payload': log['payload']

                            })

            temp_lines.append({
                'line': line,
                'logs': {
                    'smt_in': temp_smt_in_logs,
                    'smt_out': temp_smt_out_logs,
                    'packing': temp_packing_logs,
                }
            })
        # print(json.dumps(temp_lines, indent=4))
        self.logs = temp_lines

        pass

    def index_to_fill(self):
        temp_index = []

        for line in self.logs:
            temp_packing_lost_index = []
            temp_packing_index = []
            for packing_log in line['logs']['packing']:
                temp_packing_index.append(packing_log['index'])
            for i in range(24):
                if i == datetime.now().hour:
                    break
                if i not in temp_packing_index:
                    temp_packing_lost_index.append(i)

            temp_index.append(
                {
                    'line': line['line'],
                    'packing': temp_packing_lost_index
                }
            )
        print(json.dumps(temp_index, indent=4))
        return temp_index

    def post_lost_target(self):
        self.load_logs()  # load all the logs
        miss_logs_index = self.index_to_fill()  # get the misses index

        print(miss_logs_index)
        for line in self.get_lost_hours():
            print(line['line'])
            print('-----------------------------------------------------')
            for miss_target in line['hours_lost']['packing']:
                if line['line'] == 'J01':
                    print(miss_target)





        pass

    def get_lost_hours(self):
        current_hour_index = datetime.now().hour

        lost_hour = []
        for element in self.wp['lines']:
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
        return lost_hour
