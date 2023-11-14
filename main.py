import json

import requests
from scheduler import Scheduler


# for future reference, please make the API run faster! It takes forever to test

class ScheduleError(Exception):
    pass


def main():
    # set up API
    API_KEY = "61cb87f4-4052-4930-8b32-752e305a263c"
    BASE_URL = "http://scheduling-interview-2021-265534043.us-west-2.elb.amazonaws.com"
    API_PARAMS = {"token": API_KEY}
    HEADERS = {
        "accept": "*/*",
        'Content-Type': 'application/json'
    }

    # call API to start
    result = requests.post(f'{BASE_URL}/api/Scheduling/Start', params=API_PARAMS, headers=HEADERS)
    if result.status_code == 401:
        raise ScheduleError("Invalid API Key")

    # create scheduler and initalize schedule
    result = requests.get(f'{BASE_URL}/api/Scheduling/Schedule', params=API_PARAMS, headers=HEADERS)
    status_code = result.status_code
    if status_code == 401:
        raise (ScheduleError("Invalid API Key"))
    elif status_code == 405:
        raise ScheduleError("The schedule has already been retrieved for this 'run'")

    scheduler = Scheduler(result.json())

    # loop through until we no longer have appointment requests in the queue
    while True:
        result = requests.get(f'{BASE_URL}/api/Scheduling/AppointmentRequest', params=API_PARAMS, headers=HEADERS)
        status_code = result.status_code
        if status_code == 204:
            break  # we are done!!
        elif status_code == 401:
            raise (ScheduleError("Invalid API Key"))
        elif status_code == 405:
            raise ScheduleError("The schedule has already been retrieved for this 'run'")
        new_schedule_request = scheduler.schedule(result.json())
        result = requests.post(f'{BASE_URL}/api/Scheduling/Schedule', params=API_PARAMS, headers=HEADERS, data=json.dump(new_schedule_request))
        status_code = result.status_code
        if status_code == 405:
            raise ScheduleError("You already called 'stop' on this run")
        elif status_code == 500:
            raise ScheduleError(f"The schedule was unable to accommodate your requested appointment")

    # close API to signal end
    result = requests.post(f'{BASE_URL}/api/Scheduling/Stop', params=API_PARAMS, headers=HEADERS)
    if result.status_code == 401:
        raise ScheduleError("Invalid API Key")

    return


if __name__ == '__main__':
    try:
        main()
        print("Done!")
    except ScheduleError as error:
        print(f"Schedule error: {str(error)}")
    except Exception as error:
        print(f'Something went wrong! {str(error)}')
