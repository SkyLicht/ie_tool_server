import json

import requests

from src.http.get_data_from_mackenzie_api import get_day_before_outputs_data
from src.http.logs import get_current_day_lost_target_logs, post_target_loss_log
from src.http.wp_and_hours import get_wp_current_day, get_wp
from src.lib.util_config import Server, get_ip
from src.programs.logs.IEToolLogs import IEToolLogs
from src.programs.logs.target_miss import TargetMissLogs
from src.lib.util_json import json_read
from src.test.test_mackenzie_api import test_mackenzie_api


# http://127.0.0.1:8090
# user passw


def main():

    #test_mackenzie_api()
    TargetMissLogs().execute()


# TargetMissLogs().execute()


# ie_tool_log = IEToolLogs()

#    ie_tool_log.run()
# console_app = Console(ie_tool_log)
# console_app.run()


if __name__ == '__main__':
    main()
