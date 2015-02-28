
class GraphNode(object):
    """
    See GraphManager for a description of the working of the graph.

    This is a base class for nodes in the calculation graph. The key methods you
    can implement in your derived node class are:

    set_dependencies() [optional, though implemented in most nodes]
    ------------------
    You choose parent nodes whose data and calculations your node depends on here.

    When a node is first created, set_dependencies() is always called before calculate().

    All nodes that depend on parent nodes must implement this method. You can omit
    it for 'leaf' nodes which do not depend on any other nodes.

    calculate()
    -----------
    You perform your calculations here.

    Return GraphNode.CALCULATE_CHILDREN to carry on calculating further nodes in the
    graph, GraphNode.DO_NOT_CALCULATE_CHILDREN not to, for example if no output data
    has changed as a result of the calculation.

    Note: If you return DO_NOT_CALCULATE_CHILDREN, child nodes will still be calculated
          if other parent nodes have caused them to do so.

    dispose() [optional]
    ---------
    Called when a node is no longer needed in the graph. You should clean up any non-node
    resources here. Note that links to parent nodes will be automatically removed, so you
    do not need to do this yourself. If you have no non-node resources, you can omit this
    method from your node class.

    make_id(identity_param1, identity_param2, ...) [optional]
    ----------------------------------------------
    Nodes have an internal unique ID made up from their

    Quality
    -------
    """
    pass


