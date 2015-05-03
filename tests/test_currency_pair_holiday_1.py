from graph import *
from test_nodes import *
from datetime import date


def test_currency_pair_holiday_1():
    """
    We create an EUR/USD holiday node and check that it correctly tells us
    whether a date is a holiday or not.
    """
    # We create graph with a currency-pair holiday node...
    graph_manager = GraphManager()
    holiday_node = NodeFactory.get_node(
        graph_manager, None, GraphNode.GCType.NON_COLLECTABLE,
        CurrencyPairHolidayNode, "EUR/USD", date(2015, 7, 4))

    # At this point, no holidays have been set up. Quality should be good...
    graph_manager.calculate()
    assert holiday_node.is_holiday is False
    assert holiday_node.quality.is_good() is True

    # We add an EUR holiday (but not for the date we are interested in)...
    holiday_db = HolidayDatabase.get_instance()
    holiday_db.add_holiday("EUR", date(2015, 12, 25))
    graph_manager.calculate()
    assert holiday_node.is_holiday is False
    assert holiday_node.quality.is_good() is True

    # We add a USD holiday for the 4-July...
    holiday_db.add_holiday("USD", date(2015, 7, 4))
    graph_manager.calculate()
    assert holiday_node.is_holiday is True
    assert holiday_node.quality.is_good() is True

    # We remove the USD holiday...
    holiday_db.remove_holiday("USD", date(2015, 7, 4))
    graph_manager.calculate()
    assert holiday_node.is_holiday is False
    assert holiday_node.quality.is_good() is True
