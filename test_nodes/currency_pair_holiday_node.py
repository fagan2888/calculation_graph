from graph import *
from .currency_holidays_node import CurrencyHolidaysNode
from .utils import Utils


class CurrencyPairHolidayNode(GraphNode):
    """
    Manages whether a date is a holiday for a currency-pair.
    """
    def __init__(self, currency_pair, date, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The currency pair, and the two currencies that make it up...
        self.currency_pair = currency_pair
        self.currency1, self.currency2 = Utils.split_currency_pair(currency_pair)

        # The date we are checking...
        self.date = date

        # Whether this date is a holiday for the pair...
        self.is_holiday = False

        # We hold the last known data-quality, as we only calculate children
        # if the holiday or the quality has changed...
        self._previous_quality = Quality()

        # Parent nodes...
        self._currency1_holidays_node = None
        self._currency2_holidays_node = None

    def set_dependencies(self):
        """
        Adds parent nodes.
        """
        self._currency1_holidays_node = None
        self._currency2_holidays_node = None
        self._currency1_holidays_node = self.add_parent_node(CurrencyHolidaysNode, self.currency1)
        self._currency2_holidays_node = self.add_parent_node(CurrencyHolidaysNode, self.currency2)

    def calculate(self):
        """
        Called when the node needs calculating.
        """
        # It is a holiday for the pair we are managing if it is a holiday for
        # either of the currencies in the pair.

        # We find the current status, and update children only if it has
        # changed from what we held before...
        new_is_holiday = False
        if self.date in self._currency1_holidays_node.holidays:
            new_is_holiday = True
        if self.date in self._currency2_holidays_node.holidays:
            new_is_holiday = True

        if (self.is_holiday != new_is_holiday) or (self.quality != self._previous_quality):
            # The data has changed...
            self.is_holiday = new_is_holiday
            self._previous_quality.set_from(self.quality)
            return GraphNode.CalculateChildrenType.CALCULATE_CHILDREN
        else:
            # The data has not changed...
            return GraphNode.CalculateChildrenType.DO_NOT_CALCULATE_CHILDREN

