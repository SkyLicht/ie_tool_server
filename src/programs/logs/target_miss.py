import json
import asyncio
from datetime import datetime

from src.http.logs import get_current_day_lost_target_logs, post_target_loss_log
from src.http.wp_and_hours import get_wp_and_hours


class TargetMissLogs:

    def __init__(self):
        self.wp = []
        print('init target miss logs')
        self.index_pending_to_post = []  # ...
        self.LINES = ['J01', 'J02', 'J03', 'J05', 'J06', 'J07', 'J08', 'J09', 'J10', 'J11', 'J12', 'J13']

    def execute(self):
        print('execute target miss logs')
        # first step,load the miss target events

        self.load_logs()
        self.logic()
        asyncio.get_event_loop().run_until_complete(self.synchronize())
        asyncio.get_event_loop().run_until_complete(self.read())

    async def synchronize(self):  # todo
        print('current minute synchronize', datetime.now().minute)
        run = True
        while run:
            if datetime.now().second >= 58:
                run = False
            await asyncio.sleep(1)

    async def read(self):  # main even loop rename
        run = True
        await_time = 30
        count = datetime.now().minute
        # if the miunte is 1 do something
        update = False
        print('current minute', datetime.now().minute)
        while run:
            if datetime.now().minute != count:
                print(datetime.now(), ' update -> ', count, 'minute -> ', datetime.now().minute)
                update = True

            if update:
                if datetime.now().minute == 1:
                    print("it's 1")
                    print('db request')
                    self.load_logs()
                    self.logic()

            count = datetime.now().minute
            update = False
            await asyncio.sleep(await_time)

    def logic(self):
        """

        :return:
        """
        self.wp = get_wp_and_hours()
        self.post_target_miss_logs()

    def load_logs(self):
        """
        This function load the target miss log form the db;
        current date
        all the line
        TARGET_MISS
        """
        logs = get_current_day_lost_target_logs()
        temp_lines = []

        for line in self.LINES:
            temp_smt_in_logs = []
            temp_smt_out_logs = []
            temp_packing_logs = []
            # classify logs by line
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
        """
        This section transform the list log to pending index to post
    
        
        """
        temp_index = []

        for line in temp_lines:
            temp_packing_lost_index = []
            temp_packing_index = []
            for packing_log in line['logs']['packing']:
                temp_packing_index.append(packing_log['index'])
            for i in range(24):
                if i == datetime.now().hour:  # break when the index is one hour less the actual hour index
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
        self.index_pending_to_post = temp_index

    def calculate_all_the_target_miss_hours(self):  # find the lost hours
        """

        :return:
        """
        current_hour_index = datetime.now().hour
        lost_hour = []
        print('-------------------------------------------------------------')
        print(self.wp)
        for element in self.wp['lines']:

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
        print('-------------------------------------------------------------')
        print(lost_hour)
        return lost_hour

    def post_target_miss_logs(self):
        """

        :return:
        """
        miss_target_hours = self.calculate_all_the_target_miss_hours()
        for logs_to_pots in self.index_pending_to_post:
            print(logs_to_pots['line'])
            target_miss = [d['hours_lost'] for d in miss_target_hours if d['line'] == logs_to_pots['line']]
            # target_miss_smt_in = target_miss[0]['smt_in']
            # target_miss_smt_out = target_miss[0]['smt_out']
            print(target_miss)
            if len(target_miss) > 0:
                target_miss_packing = target_miss[0]['packing']
                # print(json.dumps(target_miss[0], indent=4))
                # print(target_miss_smt_in)
                # print(target_miss_smt_out)
                # print(json.dumps(target_miss_packing,indent=4))

                for log_index in logs_to_pots['packing']:
                    print(f'Searching for the hour {log_index} in target miss packing -> {target_miss_packing}')
                    hour_info = [hour for hour in target_miss_packing if hour['index'] == log_index]
                    if len(hour_info) > 0:
                        print(f'The hour {hour_info} has not events allocate ')
                        post_target_loss_log(
                            index=hour_info[0]['index'],
                            line=logs_to_pots['line'],
                            uph=hour_info[0]['uph'],
                            target=hour_info[0]['target']
                        )
                        print(f' The hour {hour_info} has been post to the db')
