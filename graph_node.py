from .graph_exception import GraphException


class GraphNode(object):
    """
    See GraphManager for a description of the working of the graph, and
    the project's website for full details: http://richard-shepherd.github.io/calculation_graph/

    This is a base class for nodes in the calculation graph. The key methods you
    can implement in your derived node class are:

    __init__(self, identity_param1, identity_param2, ...)
    -----------------------------------------------------
    Your node's identity parameters are passed to __init__.

    set_dependencies(self) [optional, though implemented in most nodes]
    ----------------------
    You choose parent nodes whose data and calculations your node depends on here.

    When a node is first created, set_dependencies() is always called before calculate().

    All nodes that depend on parent nodes must implement this method. You can omit
    it for 'leaf' nodes which do not depend on any other nodes.

    calculate(self)
    ---------------
    You perform your calculations here.

    Return GraphNode.CALCULATE_CHILDREN to carry on calculating further nodes in the
    graph, GraphNode.DO_NOT_CALCULATE_CHILDREN not to, for example if no output data
    has changed as a result of the calculation.

    Note: If you return DO_NOT_CALCULATE_CHILDREN, child nodes will still be calculated
          if other parent nodes have caused them to do so.

    dispose(self) [optional]
    -------------
    Called when a node is no longer needed in the graph. You should clean up any non-node
    resources here. Note that links to parent nodes will be automatically removed, so you
    do not need to do this yourself. If you have no non-node resources, you can omit this
    method from your node class.

    make_id(self, identity_param1, identity_param2, ...) [optional]
    ----------------------------------------------------
    Nodes have an internal unique ID made up from the node class's type name and the node's
    identity parameters. By default this is created by concatenating the string representation
    of the parameters, joining them with underscores. If you need to control how the ID is made
    you can override the make_id() method. You may wish to do this, for example, if some of the
    parameters cannot easily be stringified.

    merge_quality(self) [optional]
    -------------------
    By default, the quality of a node is found by merging the quality of all its parent nodes,
    along with any quality merged during calculate(). Sometimes, however, it is not desirable to
    merge the quality of all parent nodes. In these cases, you can implement the merge_quality()
    function to do this manually. This function is called just before calculate().


    """
    pass


