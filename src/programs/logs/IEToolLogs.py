
from src.programs.Program import Program
from src.programs.logs.target_miss import TargetMissLogs


class IEToolLogs(Program):
    def __init__(self):
        super().__init__()
        print('log created')

    def run(self):
        super().run()
        TargetMissLogs().execute()
        #HttpLiveEventsLogs().execute()






