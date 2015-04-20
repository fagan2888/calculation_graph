from graph import *
from datetime import date


class CurrencyHolidaysNode(GraphNode):
    """
    Holds holidays for a currency.
    """
    def __init__(self, currency, *args, **kwargs):
        """
        Constructor.
        """
        super().__init__(*args, **kwargs)

        # The currency...
        self.currency = currency

        # The collection of holidays...
        self.holidays = set()

    def add_holiday(self, date):
        """
        Adds a holiday date.
        """
        self.holidays.add(date)
        self.needs_calculation()

    def is_holiday(self, date):
        """
        Returns true if the date passed in is a holiday.
        """
        return date in self.holidays


class CurrencyPairHolidayNode(GraphNode):
    """
    Determines whether a date is a holiday for a currency-pair.
    """
    def __init__(self, currency1, currency2, date, *args, **kwargs):
        """
        Constructor.
        """
        super().__init__(*args, **kwargs)

        # The construction parameters...
        self.currency1 = currency1
        self.currency2 = currency2
        self.date = date

        # Parent nodes...
        self.currency1_holidays_node = None
        self.currency2_holidays_node = None

        # The result we're calculating...
        self.is_holiday = False

    def set_dependencies(self):
        """
        Adds dependencies on parent nodes.
        """
        self.currency1_holidays_node = self.add_parent_node(CurrencyHolidaysNode, self.currency1)
        self.currency2_holidays_node = self.add_parent_node(CurrencyHolidaysNode, self.currency2)

    def calculate(self):
        """
        We check if the date is a holiday.
        """
        is_currency1_holiday = self.currency1_holidays_node.is_holiday(self.date)
        is_currency2_holiday = self.currency2_holidays_node.is_holiday(self.date)
        self.is_holiday = is_currency1_holiday or is_currency2_holiday

        return GraphNode.CalculateChildrenType.CALCULATE_CHILDREN


def test_simple_graph_1():
    """
    Created a graph with three nodes, and tests that the child node
    is updated if the parents are updated.
    """
    graph_manager = GraphManager()

    # We set up some EUR holidays...
    eur_holidays_node = NodeFactory.get_node(
        graph_manager, None, GraphNode.GCType.NON_COLLECTABLE,
        CurrencyHolidaysNode,
        "EUR")
    eur_holidays_node.add_holiday(date(2015, 2, 14))
    eur_holidays_node.add_holiday(date(2014, 12, 25))

    # We set up some USD holidays...
    usd_holidays_node = NodeFactory.get_node(
        graph_manager, None, GraphNode.GCType.NON_COLLECTABLE,
        CurrencyHolidaysNode,
        "USD")
    usd_holidays_node.add_holiday(date(2015, 7, 4))
    usd_holidays_node.add_holiday(date(2015, 1, 11))
    usd_holidays_node.add_holiday(date(2014, 12, 25))

    # We create a node to tell us whether 2-Feb-2015 is a holiday...
    eur_usd_holiday_node = NodeFactory.get_node(
        graph_manager, None, GraphNode.GCType.NON_COLLECTABLE,
        CurrencyPairHolidayNode,
        "EUR", "USD", date(2015, 2, 2))

    # We calculate the graph, and check the holiday...
    graph_manager.calculate()
    assert eur_usd_holiday_node.is_holiday is False

    # We add 2-Feb-2015 as a holiday to EUR, and calculate again...
    eur_holidays_node.add_holiday(date(2015, 2, 2))
    graph_manager.calculate()
    assert eur_usd_holiday_node.is_holiday is True

    # We check that releasing nodes works.
    # First we release the parent nodes. As the child node still needs
    # them, they should remain in the graph...
    graph_manager.release_node(eur_holidays_node)
    graph_manager.release_node(usd_holidays_node)
    graph_manager.calculate()
    assert graph_manager.get_node_count() == 3

    # We now release the child node. As there are no more references to
    # any of the nodes, they should all be cleaned up...
    graph_manager.release_node(eur_usd_holiday_node)
    graph_manager.calculate()
    assert graph_manager.get_node_count() == 0
