# {
#     "doctorId": 2,
#     "personId": 1,
#     "appointmentTime": "2021-11-08T08:00:00Z",
#     "isNewPatientAppointment": false
#   },
#   {
#     "doctorId": 3,
#     "personId": 1,
#     "appointmentTime": "2021-12-15T09:00:00Z",
#     "isNewPatientAppointment": false
#   },
class Scheduler:
    def __init__(self, init_schedule: list[dict]) -> None:
        self.patient_schedules = {}
        self.doctor_schedules = {1: set(), 2: set(), 3: set()}
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
            self.patient_schedules[appt['personId']].add(appt['appointmentTime'])
            # add appt to doctor schedules (assuming that doctor is always 1, 2, or 3)
            self.doctor_schedules[appt['doctorId']].add(appt['appointmentTime'])
        return

    # This function takes in an appointment request and returns a schedule request
    def schedule(self, app_request: dict) -> dict:
        # First, need to check if the person is new.If they are, then schedule for preferred days at 3-4

        # If not new, get the days that they are currently scheduled, then schedule for preferred days that are 7 days apart.If no preferred days, then get the next available day after preferred day.(Here I need to check for out of bounds, meaning later than December and earlier than November)

        # create and return new appointment request
        pass

    # Given the proper
    def _create_new_patient_request(self, preferred_docs: list[int], preferredDays: list[str], person_id: int, request_id: int):
        pass

    def _create_curr_patient_request(self, preferred_docs: list[int], preferredDays: list[str], person_id: int, request_id: int):
        pass
