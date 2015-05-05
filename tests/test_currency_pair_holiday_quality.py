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


def test_currency_pair_holiday_quality():
    """
    Tests that quality is correctly merged through the graph.
    """
    # We create a graph with a currency-pair holiday node...
    graph_manager = GraphManager()
    graph_manager.environment = Environment()
    graph_manager.use_has_calculated_flags = True

    root_node = NodeFactory.get_node(
        graph_manager, GraphNode.GCType.NON_COLLECTABLE,
        RootNode, "EUR/USD", date(2015, 7, 4))

    # Initial quality should be good...
    graph_manager.calculate()
    holiday_node = root_node.pair_holiday_node
    assert holiday_node.quality.is_good() is True
    assert holiday_node.quality.get_description() == ""
    assert root_node.has_calculated is True

    # We set GBP holidays to have Bad quality.
    # This should not affect our node.
    holiday_db = graph_manager.environment.holiday_db
    holiday_db.set_quality("GBP", Quality.BAD, "Bad data for GBP")
    graph_manager.calculate()
    assert holiday_node.quality.is_good() is True
    assert holiday_node.quality.get_description() == ""
    assert root_node.has_calculated is False

    # We set USD holidays to have Bad quality...
    holiday_db.set_quality("USD", Quality.BAD, "Bad data for USD")
    graph_manager.calculate()
    assert holiday_node.quality.is_good() is False
    assert "Bad data for USD" in holiday_node.quality.get_description()
    assert root_node.has_calculated is True

    # We set EUR holidays to have Bad quality...
    holiday_db.set_quality("EUR", Quality.BAD, "Bad data for EUR")
    graph_manager.calculate()
    assert holiday_node.quality.is_good() is False
    assert "Bad data for USD" in holiday_node.quality.get_description()
    assert "Bad data for EUR" in holiday_node.quality.get_description()
    assert root_node.has_calculated is True

    # We set EUR holidays Good...
    holiday_db.set_quality("EUR", Quality.GOOD, "")
    graph_manager.calculate()
    assert holiday_node.quality.is_good() is False
    assert "Bad data for USD" in holiday_node.quality.get_description()
    assert "Bad data for EUR" not in holiday_node.quality.get_description()
    assert root_node.has_calculated is True

    # We set USD holidays Good...
    holiday_db.set_quality("USD", Quality.GOOD, "")
    graph_manager.calculate()
    assert holiday_node.quality.is_good() is True
    assert holiday_node.quality.get_description() == ""
    assert root_node.has_calculated is True

    # We set an info message for USD...
    holiday_db.set_quality("USD", Quality.GOOD, "Info: USD data stale")
    graph_manager.calculate()
    assert holiday_node.quality.is_good() is True
    assert "Info: USD data stale" in holiday_node.quality.get_description()
    assert root_node.has_calculated is True


