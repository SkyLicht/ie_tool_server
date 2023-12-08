import json
import asyncio
from datetime import datetime

from src.http.logs import get_current_day_lost_target_logs, post_target_loss_log, Area
from src.http.wp_and_hours import get_wp




class TargetMissLogs:
    def __init__(self):
        self.index_pending_to_post = []
        self.LINES = ['J01', 'J02', 'J03', 'J05', 'J06', 'J07', 'J08', 'J09', 'J10', 'J11', 'J12', 'J13']

    def execute(self):
        print('execute target miss logs')
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
        # if the minute is 1 do something
        update = False
        print('current minute', datetime.now().minute)
        while run:
            if datetime.now().minute != count:
                print(datetime.now(), ' update -> ', count, 'minute -> ', datetime.now().minute)
                update = True

            if update:
                if datetime.now().minute == 1:
                    print('db request')
                    self.logic()

            count = datetime.now().minute
            update = False
            await asyncio.sleep(await_time)

    def logic(self):
        self.load_logs()
        self.calculate_all_the_target_miss_hours()
        self.post_target_miss_logs()
        pass

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
            temp_smt_out_lost_index = []
            temp_smt_out_index = []
            for smt_our_logs in line['logs']['smt_out']:
                temp_smt_out_index.append(smt_our_logs['index'])
            for i in range(24):
                if i == datetime.now().hour:  # break when the index is one hour less the actual hour index
                    break
                if i not in temp_smt_out_index:
                    temp_smt_out_lost_index.append(i)

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
                    'smt_out': temp_smt_out_lost_index,
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
        wp = get_wp()
        lost_hour = []
        print('work plan ---->')
        for element in wp:
            uph_target = element.uph_i

            target_lost = {
                "smt_in": [],
                "smt_out": [],
                "packing": []
            }

            for hour in element.hour:
                if hour.index < current_hour_index:
                    if hour.smt_in < uph_target:
                        target_lost['smt_in'].append(
                            {"index": hour.index, "uph": hour.smt_in, "target": uph_target})

            for hour in element.hour:
                if hour.index < current_hour_index:
                    if hour.smt_out < uph_target:
                        target_lost['smt_out'].append(
                            {"index": hour.index, "uph": hour.smt_out, "target": uph_target})

            for hour in element.hour:
                if hour.index < current_hour_index:
                    if hour.packing < uph_target:
                        target_lost['packing'].append(
                            {"index": hour.index, "uph": hour.packing, "target": uph_target})
            lost_hour.append({
                "line": element.line,
                "hours_lost": target_lost
            })
        print('-------------------------------------------------------------')
        print(json.dumps(lost_hour, indent=4))
        return lost_hour

    def post_target_miss_logs(self):
        """

        :return:
        """
        miss_target_hours = self.calculate_all_the_target_miss_hours()
        for logs_to_pots in self.index_pending_to_post:
            print(logs_to_pots['line'])
            target_miss = [d['hours_lost'] for d in miss_target_hours if d['line'] == logs_to_pots['line']]

            if len(target_miss) > 0:
                print('data')
                target_miss_smt_in = target_miss[0]['smt_in']
                target_miss_smt_out = target_miss[0]['smt_out']
                target_miss_packing = target_miss[0]['packing']

                for log_index in logs_to_pots['smt_out']:
                    print(f'Searching for the hour {log_index} in target miss smt out -> {target_miss_smt_out}')
                    hour_info = [hour for hour in target_miss_smt_out if hour['index'] == log_index]
                    if len(hour_info) > 0:
                        post_target_loss_log(
                            area=Area.SMT_OUT,
                            index=hour_info[0]['index'],
                            line=logs_to_pots['line'],
                            uph=hour_info[0]['uph'],
                            target=hour_info[0]['target']
                        )
                        print(f' The hour {hour_info} has been post to the db')

                for log_index in logs_to_pots['packing']:
                    print(f'Searching for the hour {log_index} in target miss packing -> {target_miss_packing}')
                    hour_info = [hour for hour in target_miss_packing if hour['index'] == log_index]
                    if len(hour_info) > 0:
                        post_target_loss_log(
                            area=Area.PACKING,
                            index=hour_info[0]['index'],
                            line=logs_to_pots['line'],
                            uph=hour_info[0]['uph'],
                            target=hour_info[0]['target']
                        )
                        print(f' The hour {hour_info} has been post to the db')
