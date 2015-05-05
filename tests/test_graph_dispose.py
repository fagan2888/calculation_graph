from graph import *
from test_nodes import *
from datetime import date


class TestNode(GraphNode):
    """
    A node that notes when it has been disposed.
    """
    def __init__(self, text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = text
        self.is_disposed = False

    def dispose(self):
        self.is_disposed = True


def test_graph_dispose():
    """
    Disposes a graph and checks that all nodes have been cleaned up.
    """
    graph_manager = GraphManager()
    graph_manager.environment = Environment()

    # We add a number of nodes...

    # 3 nodes...
    pair_holiday_node_1 = NodeFactory.get_node(
        graph_manager, GraphNode.GCType.NON_COLLECTABLE,
        CurrencyPairHolidayNode, "EUR/USD", date(2015, 2, 3))

    # 2 nodes...
    pair_holiday_node_2 = NodeFactory.get_node(
        graph_manager, GraphNode.GCType.NON_COLLECTABLE,
        CurrencyPairHolidayNode, "GBP/USD", date(2015, 3, 4))

    # 1 node...
    test_node_1 = NodeFactory.get_node(
        graph_manager, GraphNode.GCType.NON_COLLECTABLE,
        TestNode, "TestNode1")

    # Note: This should be the same as test_node_1...
    test_node_2 = NodeFactory.get_node(
        graph_manager, GraphNode.GCType.NON_COLLECTABLE,
        TestNode, "TestNode1")
    assert test_node_1 is test_node_2

    # 1 node...
    test_node_3 = NodeFactory.get_node(
        graph_manager, GraphNode.GCType.NON_COLLECTABLE,
        TestNode, "TestNode3")

    graph_manager.calculate()
    assert len(graph_manager._nodes) == 7

    # We dispose the graph...
    graph_manager.dispose()
    assert len(graph_manager._nodes) == 0
    assert test_node_1.is_disposed is True
    assert test_node_2.is_disposed is True
    assert test_node_3.is_disposed is True



