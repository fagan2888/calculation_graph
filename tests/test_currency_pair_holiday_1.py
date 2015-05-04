from graph import *
from test_nodes import *
from datetime import date


class RootNode(GraphNode):
    """
    Root node for this test. It gets a pair-holiday from a parent
    CurrencyPairHolidayNode and lets us check if the parent has
    caused this node to calculate (ie, if the holiday has changed).
    """
    def __init__(self, currency_pair, date, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.currency_pair = currency_pair
        self.date = date
        self.pair_holiday_node = None

    def set_dependencies(self):
        self.pair_holiday_node = self.add_parent_node(CurrencyPairHolidayNode, self.currency_pair, self.date)


def test_currency_pair_holiday_1():
    """
    We create an EUR/USD holiday node and check that it correctly tells us
    whether a date is a holiday or not.
    """
    holiday_db = HolidayDatabase.get_instance()
    holiday_db.clear()

    # We create a graph with a currency-pair holiday node...
    graph_manager = GraphManager()
    graph_manager.use_has_calculated_flags = True
    root_node = NodeFactory.get_node(
        graph_manager, None, GraphNode.GCType.NON_COLLECTABLE,
        RootNode, "EUR/USD", date(2015, 7, 4))

    # At this point, no holidays have been set up. Quality should be good...
    graph_manager.calculate()
    holiday_node = root_node.pair_holiday_node
    assert holiday_node.is_holiday is False
    assert root_node.has_calculated is True

    # We add an EUR holiday (but not for the date we are interested in),
    # so our node should not be calculated.
    holiday_db.add_holiday("EUR", date(2015, 12, 25))
    graph_manager.calculate()
    assert holiday_node.is_holiday is False
    assert root_node.has_calculated is False

    # We add a GBP holiday. This should have no effect on the holiday,
    # and the node should not have calculated...
    holiday_db.add_holiday("GBP", date(2015, 7, 4))
    graph_manager.calculate()
    assert holiday_node.is_holiday is False
    assert root_node.has_calculated is False

    # We add a USD holiday for the 4-July...
    holiday_db.add_holiday("USD", date(2015, 7, 4))
    graph_manager.calculate()
    assert holiday_node.is_holiday is True
    assert root_node.has_calculated is True

    # We remove the USD holiday...
    holiday_db.remove_holiday("USD", date(2015, 7, 4))
    graph_manager.calculate()
    assert holiday_node.is_holiday is False
    assert root_node.has_calculated is True
