from .holiday_database import HolidayDatabase


class Environment(object):
    """
    Holds data that we pass to all the nodes.
    """
    def __init__(self):
        self.holiday_db = HolidayDatabase()
