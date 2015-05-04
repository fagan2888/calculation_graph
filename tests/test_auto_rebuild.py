from graph import *
from test_nodes import *
from datetime import date


class PriceForHoliday(GraphNode):
    """
    Calculates the price for a holiday.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = 123.0


class PriceForNonHoliday(GraphNode):
    """
    Calculates the price for a holiday.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = 456.0


class Price(GraphNode):
    """
    Calculates a 'price' depending one whether a date is a holiday or not.
    It uses different parent nodes in each case.
    """
    def __init__(self, currency_pair, date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currency_pair = currency_pair
        self.date = date

        # Parent nodes...
        self.holiday_node = None
        self.price_node = None

        # The result...
        self.price = 0.0

    def set_dependencies(self):
        # We find whether the date we are managing is a holiday...
        self.holiday_node = self.add_parent_node(CurrencyPairHolidayNode, self.currency_pair, self.date)

        # We use a different price node depending on whether the date is a holiday or not...
        if self.holiday_node.is_holiday is True:
            self.price_node = self.add_parent_node(PriceForHoliday)
        else:
            self.price_node = self.add_parent_node(PriceForHoliday)

    def calculate(self):
        # We get the price from the active price node...
        self.price = self.price_node.price


def test_auto_rebuild():
    """
    Tests that nodes automatically rebuild dependencies if specified
    parent nodes have changed.

    In this example we have one calculation which is used if a date is
    a holiday and another for a non-holiday.

    We change the holiday information, and check that the nodes are
    hooked up correctly.
    """
    pass
