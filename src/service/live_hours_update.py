import asyncio
import time
from datetime import datetime, timedelta

from src.http.day_and_hours_update import post_day_and_hours_day_before
from src.http.get_data_from_mackenzie_api import get_current_day_outputs_data, get_day_before_outputs_data
from src.http.live_hours import live_update_hour, live_update_day, clean_live_db


def run():  # main even loop rename
    while True:
        if datetime.now().hour == 0:
            clean_live_hours()
        if datetime.now().hour == 1:
            update_the_day_before()
        if datetime.now().minute == 1:
            print('one hours has passed', datetime.now().minute)
            update_hour()
        # Get the current time
        now = datetime.now()
        # Calculate the time until the next minute
        next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
        time_until_next_minute = (next_minute - now).total_seconds()

        # Execute the function every minute
        print('minutes passed -> ', datetime.now().minute)

        #update_minute()
        #update_the_day_before()
        time.sleep(time_until_next_minute)


def update_hour():
    mackenzie_api = get_current_day_outputs_data()
    live_update_day(mackenzie_api)
    pass


def clean_live_hours():
    clean_live_db()


def update_minute():
    mackenzie_api = get_current_day_outputs_data()
    live_update_hour(mackenzie_api)
    pass


def update_the_day_before():
    mackenzie_api = get_day_before_outputs_data()
    post_day_and_hours_day_before(mackenzie_api)
    pass


def live_hours_update_run():
    run()
    pass
