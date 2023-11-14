from datetime import datetime
from schedule_error import ScheduleError

# 2021-11-14T22:27:13.556Z
DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
SET_DATE_FORMAT = '%Y-%m-%dT%H'


class Scheduler:
    def __init__(self, init_schedule: list[dict]) -> None:
        self.patient_schedules = {}
        self.doctor_schedules = {1: set(), 2: set(), 3: set()}
        print(init_schedule)
        self._fill_schedules(init_schedule)
        print(self.patient_schedules)
        print(self.doctor_schedules)

    def _fill_schedules(self, init_schedule: list[dict]):
        # loop through list of previous appointments
        for appt in init_schedule:
            # add appt to person schedules
            # if the person is not in the patient dict then make new list
            if appt['personId'] not in self.patient_schedules:
                self.patient_schedules[appt['personId']] = set()
            self.patient_schedules[appt['personId']].add(
                datetime.strptime(appt['appointmentTime'], DATE_FORMAT).strftime(SET_DATE_FORMAT))
            # add appt to doctor schedules (assuming that doctor is always 1, 2, or 3)
            self.doctor_schedules[appt['doctorId']].add(
                datetime.strptime(appt['appointmentTime'], DATE_FORMAT).strftime(SET_DATE_FORMAT))
        return

    def schedule(self, app_request: dict) -> dict:
        # First, need to check if the person is new.If they are, then schedule for preferred days at 3-4
        schedule_request = None
        if app_request['isNew']:
            schedule_request = self._create_new_patient_request(app_request['preferredDocs'],
                                                                app_request['preferredDays'],
                                                                app_request['personId'], app_request['requestId'])
        # If not new, get the days that they are currently scheduled, then schedule for preferred days that are 7 days apart.If no preferred days, then get the next available day after preferred day.(Here I need to check for out of bounds, meaning later than December and earlier than November)
        else:
            schedule_request = self._create_curr_patient_request(app_request['preferredDocs'],
                                                                 app_request['preferredDays'],
                                                                 app_request['personId'], app_request['requestId'])
        if schedule_request is None:
            raise ScheduleError("Never made a schedule request!")
        # create and return new appointment request
        return schedule_request

    # this function will handle a new patient request to the patient and return a dictionary with the schedule request
    def _create_new_patient_request(self, preferred_docs: list[int], preferred_days: list[str], person_id: int,
                                    request_id: int):
        # since this person doesn't have any appointments yet, we can just look for the next open date
        # that their preferred doctor has open
        # loop through the doctors and find one that has an availability on the preferred days
        schedule_date = None
        scheduled_doc = None
        for doc in preferred_docs:
            for pref_day_str in preferred_days:
                # check 3:00
                pref_day = datetime.strptime(pref_day_str, DATE_FORMAT).replace(hour=15)
                # if it is a weekend, then we don't schedule!
                if self._can_schedule(pref_day):
                    continue
                if pref_day.strftime(SET_DATE_FORMAT) not in self.doctor_schedules[doc]:
                    schedule_date = pref_day
                    scheduled_doc = doc
                    break
                # check 4:00
                pref_day = pref_day.replace(hour=16)
                if pref_day.strftime(SET_DATE_FORMAT) not in self.doctor_schedules[doc]:
                    schedule_date = pref_day
                    scheduled_doc = doc
                    break
            # if we have found a viable schedule date, then we break
            if schedule_date:
                break
        # if nothing lines up on preferred days, then exit? It wasn't clear what to do on this case.
        # if needed, we could loop over and find the next available 3:00 or 4:00 appointment for the given doctor
        if schedule_date is None or scheduled_doc is None:
            raise ScheduleError("No open times for preferred dates!")
        # add to our doctor and patient dicts
        self.doctor_schedules[scheduled_doc].add(schedule_date.strftime(SET_DATE_FORMAT))
        # got to add a new entry, as we haven't seen this person before
        self.patient_schedules[person_id] = set()
        self.patient_schedules[person_id].add(schedule_date.strftime(SET_DATE_FORMAT))
        return {
            'doctorId': scheduled_doc,
            'personId': person_id,
            'appointmentTime': schedule_date.strftime(DATE_FORMAT),
            'isNewPatientAppointment': True,
            'requestId': request_id
        }

    def _create_curr_patient_request(self, preferred_docs: list[int], preferred_days: list[str], person_id: int,
                                     request_id: int):
        schedule_date = None
        scheduled_doc = None
        for doc in preferred_docs:
            for pref_day_str in preferred_days:
                pref_day = datetime.strptime(pref_day_str, DATE_FORMAT)
                # if it is a weekend, out of range, or within then we don't schedule!
                if self._can_schedule(pref_day, person_id):
                    continue
                # check each hour to schedule appt
                for hour in range(8, 15):
                    if pref_day.replace(hour=hour).strftime(SET_DATE_FORMAT) not in self.doctor_schedules[doc]:
                        schedule_date = pref_day
                        scheduled_doc = doc
                        break
                # if we have found an appt then break
                if schedule_date is not None:
                    break
            if schedule_date is not None:
                break
        # if nothing lines up on preferred days, then exit? It wasn't clear what to do on this case.
        # if needed, we could loop over and find the next available day for their preferred doctor to have an appointment
        if schedule_date is None or scheduled_doc is None:
            raise ScheduleError("No open times for preferred dates!")
        # add to our doctor and patient dicts
        self.doctor_schedules[scheduled_doc].add(schedule_date.strftime(SET_DATE_FORMAT))
        self.patient_schedules[person_id].add(schedule_date.strftime(SET_DATE_FORMAT))
        return {
            'doctorId': scheduled_doc,
            'personId': person_id,
            'appointmentTime': schedule_date.strftime(DATE_FORMAT),
            'isNewPatientAppointment': False,
            'requestId': request_id
        }

    def _can_schedule(self, day, person_id=None):
        if day.isoweekday():
            return False
        if day > datetime(2022, 1, 1):
            return False
        if day < datetime(2021, 11, 1):
            return False
        if person_id:
            for appt in self.patient_schedules[person_id]:
                date = datetime.strptime(appt['appointmentTime'], DATE_FORMAT)
                if day > date and day - date < 7:
                    return False
                elif day < date and date - day < 7:
                    return False
        return True

