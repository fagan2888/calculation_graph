
class GrapManager(object):
    """
    The GraphManager manages a 'directed acyclic graph' of nodes and recalculates
    them efficiently as the inputs to those nodes changes.

    The graph is built by adding nodes using the add_node() method. The add_parent()
    method, within the GraphNode class, is used to indicate that a nodes depends on
    some other node. The needs_calculation() method of this class is used to indicate
    that the output value of the specified node must be calculated the next time the
    graph is calculated.

    When the GraphManager determines that a node needs calculation, its calculate()
    method is called. This will only be called after any parent nodes have been
    calculated. So the parent data needed by any node will always be up-to-date at
    the point that its calculate() method is called.

    Calculation order of nodes
    --------------------------
    Calculation order is worked out like this:

    On calling 'calculate' on this class, the invalidate() method is called on each
    node for which needs_calculation() has been called since the last invocation of
    calculate(). The invalidate() method of the graph node, increments an
    invalidation counter within the node, and then recursively calls invalidate()
    on any nodes which have specified the current node as a parent.

    The calculate() method for this class then calls the validate() method on each
    node that it called invalidate() on. The validate() method of the graph node
    decrements the invalidation counter for the node and, if the resultant counter
    value is zero, calls the calculate() method for the class. This means that a node
    will only be calculated when all routes to it have been calculated.

    The invalidation count on a node is initialized to zero when the node is
    constructed and should always be zero on completion of the graph calculate()
    method.

    Not thread-safe
    ---------------
    The GraphManager is not thread safe. The graph must not be concurrently
    modified by multiple threads.

    Garbage collection
    ------------------
    The GraphManager implements its own 'garbage-collection' of unused nodes.

    Even though Python has its own GC, it is not guaranteed to run as soon as
    a node is no longer needed. The GC here calls the dispose() method on a
    node when it is no longer referred to by any other nodes, to make sure it
    does not perform any calculations or consume resources when it is no longer
    an active part of the graph.

    Important seed nodes should be marked as GraphNode.GCType.NON_COLLECTABLE. You
    can do this either when you create them with GraphManager.get_node() or after
    creating them by calling set_gc_type(GraphNode.GCType.NON_COLLECTABLE) on a node.

    GC will only happen after links between nodes have been broken. This happens
    when you call remove_parent() or remove_parents() on a node. When this happens,
    the GC will take place after the next graph calculation.

    The GC algorithm starts with the set of non-collectable nodes, and finds
    all parent nodes. These will not be collected. Any remaining nodes will be
    removed from the graph and disposed.

    To remove nodes from the graph, you should call remove_node(). This marks the
    node as COLLECTABLE and allows it to be collected at the next GC cycle.
    Note: If it is used by other non-collectable nodes, it will not be deleted.

    Handling graph shape-changes during calculation
    -----------------------------------------------
    Sometimes the graph changes shape while it is calculating. Some nodes reset
    their dependencies as part of the calculation cycle in response to parent
    nodes updating. We need to calculate the graph correctly in these cases.

    If a node connects to a parent during the calculation cycle, the graph may
    not be calculated in the right order during that cycle. To ensure that the
    graph is calculated correctly we perform this logic:

    1. When nodes reset their dependencies they note which parent nodes
    were added, and register this with the graph-manager.

    2. The graph-manager keeps a map of new-parent-nodes to the child-nodes
    they have been added to.

    3. As nodes are calculated, they notify the graph-manager. If the node is
    a new-parent, then it has been calculated too late during this cycle.
    This node is a 'late-parent'.

    4. For late-parents, we find the collection of child-nodes that added them
    in this cycle. We mark these nodes for calculation in the next cycle.
    These nodes are 'early-children'.

    5. When we calculate the early-children in the next cycle, we make sure that
    their late-parents are included in their parents-updated list. This ensures
    that anything that should be triggered by the parent node updating is
    triggered.
    """
    pass

