from graph import *
from .observable import Observable


class HolidayDatabase(Observable):
    """
    Holds collections of holidays (with quality) keyed by currency.

    This class is a singleton.
    """

    # The singleton instance...
    _instance = None

    class CurrencyHolidays(object):
        """
        Holds a collection of holidays for one currency.
        """
        def __init__(self, currency):
            """
            Constructor.
            """
            # The currency...
            self.currency = currency

            # A set of holiday dates for the currency...
            self.holidays = set()

            # The quality of the data...
            self.quality = Quality()

    def __init__(self):
        """
        Constructor.
        """
        super().__init__()

        # A dictionary of CurrencyHoliday objects, keyed by currency...
        self._holidays = {}

    @staticmethod
    def get_instance():
        """
        Returns the singleton instance.
        """
        if HolidayDatabase._instance is None:
            HolidayDatabase._instance = HolidayDatabase()
        return HolidayDatabase._instance

    def add_holiday(self, currency, holiday):
        """
        Adds a holiday to the collection for the currency.
        """
        currency_holidays = self.get_currency_holidays(currency)
        currency_holidays.holidays.add(holiday)
        self.update_observers()

    def remove_holiday(self, currency, holiday):
        """
        Removes a holiday from the collection for the currency.
        """
        currency_holidays = self.get_currency_holidays(currency)
        currency_holidays.holidays.remove(holiday)
        self.update_observers()

    def set_quality(self, currency, quality, description):
        """
        Sets the data-quality for a currency.
        """
        currency_holidays = self.get_currency_holidays(currency)
        currency_holidays.quality.clear_to_good()
        currency_holidays.quality.merge(quality, description)
        self.update_observers()

    def clear(self):
        """
        Clears the collection of holidays.
        """
        self._holidays.clear()

    def get_currency_holidays(self, currency):
        """
        Finds or creates the CurrencyHolidays object for the currency passed in.
        """
        if currency in self._holidays:
            return self._holidays[currency]

        # We need to create a CurrencyHolidays object for this currency...
        currency_holidays = HolidayDatabase.CurrencyHolidays(currency)
        currency_holidays.quality.clear_to_good()
        self._holidays[currency] = currency_holidays
        return currency_holidays
