
class GraphNode(object):
    """
    See GraphManager for a description of the working of the graph.

    Methods to implement in derived classes
    ---------------------------------------
    This is a base class for nodes in the calculation graph. The main methods
    that you implement in your derived nodes are:

    - set_dependencies(): You choose parent nodes whose data and calculations
                          your node depends on here.

    - calculate(): You perform your calculations here.

    - dispose(): Called when a node is no longer needed in the graph. You should
                 clean up any non-node resources here. Note that links to parent
                 nodes will be automatically removed, so you do not need to do this
                 yourself.



    Quality
    -------
    """
    pass


