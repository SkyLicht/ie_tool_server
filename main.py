from src.http.logs import get_current_day_lost_target_logs, post_target_loss_log
from src.http.wp_and_hours import get_wp_current_day, get_wp_and_hours
from src.programs.logs.IEToolLogs import IEToolLogs
from src.programs.logs.target_miss import TargetMissLogs


# http://127.0.0.1:8090
# user passw

def main():

    TargetMissLogs().execute()



# ie_tool_log = IEToolLogs()

#    ie_tool_log.run()
    # console_app = Console(ie_tool_log)
    # console_app.run()






if __name__ == '__main__':
    main()
