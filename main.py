import json
import requests
from scheduler import Scheduler
from schedule_error import ScheduleError


# this function calls endpoints
def main():
    # set up API
    API_KEY = "61cb87f4-4052-4930-8b32-752e305a263c"
    BASE_URL = "http://scheduling-interview-2021-265534043.us-west-2.elb.amazonaws.com"
    API_PARAMS = {"token": API_KEY}
    HEADERS = {
        "accept": "*/*",
        'Content-Type': 'application/json'
    }
    session = requests.Session()

    # call API to start
    result = session.post(f'{BASE_URL}/api/Scheduling/Start', params=API_PARAMS, headers=HEADERS)
    if result.status_code == 401:
        raise ScheduleError("Invalid API Key")

    # create scheduler and initalize schedule
    print("started")
    result = session.get(f'{BASE_URL}/api/Scheduling/Schedule', params=API_PARAMS, headers=HEADERS)
    status_code = result.status_code
    if status_code == 401:
        raise (ScheduleError("Invalid API Key"))
    elif status_code == 405:
        raise ScheduleError("The schedule has already been retrieved for this 'run'")

    scheduler = Scheduler(result.json())

    # loop through until we no longer have appointment requests in the queue
    while True:
        # send request to get the appointment
        result = session.get(f'{BASE_URL}/api/Scheduling/AppointmentRequest', params=API_PARAMS, headers=HEADERS)
        status_code = result.status_code
        if status_code == 204:
            break  # we are done!!
        elif status_code == 401:
            raise (ScheduleError("Invalid API Key"))
        elif status_code == 405:
            raise ScheduleError("The schedule has already been retrieved for this 'run'")

        # parse the appointment and get back a schedule request
        new_schedule_request = scheduler.schedule(result.json())

        # send schedule request to API
        result = session.post(f'{BASE_URL}/api/Scheduling/Schedule', params=API_PARAMS, headers=HEADERS,
                              data=json.dumps(new_schedule_request))
        status_code = result.status_code
        if status_code == 405:
            raise ScheduleError("You already called 'stop' on this run")
        elif status_code == 500:
            print(f'Patient {scheduler.patient_schedules}, Doc {scheduler.doctor_schedules}')
            raise ScheduleError(
                f"The schedule was unable to accommodate your requested appointment {new_schedule_request}")

    # close API to signal end
    result = session.post(f'{BASE_URL}/api/Scheduling/Stop', params=API_PARAMS, headers=HEADERS)
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
