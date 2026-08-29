from enum import Enum

class Frequency(str, Enum):
    daily = "daily"
    twice_daily = "twice_daily"
    three_times_daily = "three_times_daily"
    



class MedicationStatus(str, Enum):
    active = "active"
    completed = "completed"
    abandoned = "abandoned"


class LogStatus(str, Enum):
    taken = "taken"
    skipped = "skipped"
    missed = "missed"