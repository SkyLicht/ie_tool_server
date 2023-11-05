from src.http.read_logs import get_current_day_lost_target_logs
from src.programs.logs.IEToolLogs import IEToolLogs


# http://127.0.0.1:8090
# user passw

def main():
    ie_tool_log = IEToolLogs()

    ie_tool_log.run()
    # console_app = Console(ie_tool_log)
    # console_app.run()




if __name__ == '__main__':
    main()
