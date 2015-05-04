from graph import *
from test_nodes import *
from datetime import date


def test_nodes_no_longer_used():
    """
    Tests that nodes are cleaned up when they are no longer needed.
    """
    holiday_db = HolidayDatabase.get_instance()
    holiday_db.clear()

    graph_manager = GraphManager()

    # We create a EUR/USD holiday node. There should be three nodes in
    # the graph, ie EUR/USD, EUR and USD...
    eur_usd_node = NodeFactory.get_node(
        graph_manager, None, GraphNode.GCType.NON_COLLECTABLE,
        CurrencyPairHolidayNode, "EUR/USD", date(2015, 4, 5))
    graph_manager.calculate()
    assert len(graph_manager._nodes) == 3

    # We create a GBP/USD node. This will add two nodes: GBP/USD and GBP.
    # The USD node should be shared.
    gbp_usd_node_1 = NodeFactory.get_node(
        graph_manager, None, GraphNode.GCType.NON_COLLECTABLE,
        CurrencyPairHolidayNode, "GBP/USD", date(2015, 5, 6))
    graph_manager.calculate()
    assert len(graph_manager._nodes) == 5

    # We add a GBP/USD node for a different date. This adds one node,
    # and shares the rest...
    gbp_usd_node_2 = NodeFactory.get_node(
        graph_manager, None, GraphNode.GCType.NON_COLLECTABLE,
        CurrencyPairHolidayNode, "GBP/USD", date(2015, 6, 7))
    graph_manager.calculate()
    assert len(graph_manager._nodes) == 6

    # We release the EUR/USD node. This should release the node itself
    # and the EUR node. The USD node should still be shared...
    graph_manager.release_node(eur_usd_node)
    graph_manager.calculate()
    assert len(graph_manager._nodes) == 4

    # We release one of the GBP/USD nodes. This just removes the node
    # as its parents are shared...
    graph_manager.release_node(gbp_usd_node_1)
    graph_manager.calculate()
    assert len(graph_manager._nodes) == 3

    # We release the other GBP/USD node. There should be no nodes left
    # in the graph...
    graph_manager.release_node(gbp_usd_node_2)
    graph_manager.calculate()
    assert len(graph_manager._nodes) == 0
