
class GraphNode(object):
    """
    Base class for nodes in the calculation graph.

    See: http://richard-shepherd.github.io/calculation_graph/GraphNode.html
    """

    # 'enum' values for node GC collectability...
    COLLECTABLE = "collectable"  # Node can be GC'd if not referred to by other nodes.
    NON_COLLECTABLE = "non collectable"  # Node will not be GC'd, even if not referred to by other nodes.



