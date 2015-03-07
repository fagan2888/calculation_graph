from .graph_exception import GraphException


# noinspection PyProtectedMember
class GraphNode(object):
    """
    Base class for nodes in the calculation graph.

    See: http:#richard-shepherd.github.io/calculation_graph/GraphNode.html
    """

    # 'enum' for node GC collectability...
    class GCType(object):
        COLLECTABLE = 1      # Node can be GC'd if not referred to by other nodes.
        NON_COLLECTABLE = 2  # Node will not be GC'd, even if not referred to by other nodes.

    #'enum' for whether child nodes should be calculated after the current node has finished calculating...
    class CalculateChildrenType(object):
        CALCULATE_CHILDREN = 1
        DO_NOT_CALCULATE_CHILDREN = 2

    def __init__(self):
        """
        The 'constructor'.
        """
        # The node's unique ID in the graph...
        self.node_id = ""

        # The graph manager...
        self.graph_manager = None

        # The environment. This can be any object useful for the particular application
        # which this graph and its nodes are used for...
        self.environment = None

        # The set of parent nodes...
        self._parents = set()

        # The set of child nodes...
        self._children = set()

        # The set of child nodes to be calculated during one calculation cycle.
        # When we calculate, we first take a copy of the _children (above), as
        # the set may change during calculation...
        self._calc_children = set()

        # The number of parent nodes which have caused this node to calculate during
        # one calculation cycle...
        self._invalid_count = 0

        # True if this node is marked for calculation in the next cycle...
        self._needs_calculation = True

        # The set of parent nodes that caused this node to calculate in
        # the current calculation cycle...
        self._updated_parent_nodes = set()

        # Garbage collection...
        self._gc_type = GraphNode.GCType.COLLECTABLE
        self._gc_ref_count = 0

    def cleanup(self):
        """
        Cleans up the node and calls dispose() on derived classes.
        """
        self.remove_parents()
        self.remove_children()
        self.dispose()

    def dispose(self):
        """
        Should be implemented by derived classes, if there are any non-node
        resources to be cleaned up.
        """
        pass

    def get_type(self):
        """

        """

    def set_dependencies(self):
        """
        Should be implemented by derived classes, if they depend on any parent nodes.
        """
        pass

    def calculate(self):
        """
        Must be implemented by derived classes.
        """
        raise GraphException("calculate() must be implemented by classes derived from GraphNode")

    def get_info_message(self):
        """
        Should be implemented by derived classes, if you want to provide graph-dump
        information about your node.
        """
        return ""

    def add_parent(self, node):
        """
        Adds a parent node for this node and updates the child node collection
        of the parent
        """
        if node not in self._parents:
            self._parents.add(node)
            node._children.add(self)

    def remove_parent(self, node):
        """
        Removes a parent node for this node and update the child node collection
        of the parent.
        """
        if node not in self._parents:
            return  # The node passed in is not one of our parent nodes.

        # We remove the parent, and remove us as a child from the parent...
        self._parents.remove(node)
        node._children.remove(self)

        # We mark the graph as needing garbage collection, as removing
        # the parent link may leave unreferenced nodes...
        self.graph_manager.link_removed()

    def remove_parents(self):
        """
        Removes all parent nodes for this node, also updates the child collections
        of the parents.
        """
        while len(self._parents) > 0:
            node = self._parents.pop()
            node._children.remove(self)

        # We mark the graph as needing garbage collection, as removing
        # the parents may leave unreferenced nodes...
        self.graph_manager.link_removed()

    def remove_children(self):
        """
        Removes all child nodes for this node, also updates the parent collections
        of the children.
        """
        while len(self._children) > 0:
            node = self._children.pop()
            node._parents.remove(self)

    def has_children(self):
        """
        True if this node has any child nodes.
        """
        return len(self._children) > 0

    def invalidate(self, parent):
        """
        Marks this node as invalid and, if this is the first invalidation, mark all
        direct child nodes as invalid.

        The parent node that is marking this node as needing calculation is passed
        in, so that nodes can see who triggered them to calculate.
        """
        # We add the parent to the collection of nodes that caused us to
        # recalculate. (If this is one of the 'root' changed nodes for this
        # calculation, the parent will be NULL, so we don't include it.)
        if parent is not None:
            self.add_updated_parent(parent)

        self._invalid_count += 1
        if self._invalid_count == 1:
            # We have just gone invalid.

            # Capture child set, as this may change as a result of calculation, and
            # make recursive call for each node in captured child set
            self._calc_children = self._children.copy()
            for node in self._calc_children:
                node.invalidate(self)

    def validate(self):
        """
        Called when one of the parent nodes has been calculated. We decrease the
        invalidation count and if it has gone to zero, then all parents have been
        calculated and we can calculate this node.

        We then notify child nodes that they need to be calculated (by calling
        validate on them).
        """
        if self._invalid_count <= 0:
            # Something has gone badly wrong in invalidate/validate...
            raise GraphException(self.node_id + ": Invalidation count is unexpectedly non-positive")

        self._invalid_count -= 1
        if self._invalid_count == 0:
            # All our parents are now valid, so we calculate our
            # output value if necessary...
            calculate_children = GraphNode.CalculateChildrenType.DO_NOT_CALCULATE_CHILDREN
            if self._needs_calculation is True:
                calculate_children = self.calculate()
                self._needs_calculation = False

                # We tell the graph-manager that the node has been calculated...
                self.graph_manager.node_calculated(self)

            # We calculate our child nodes...
            for child_node in self._calc_children:
                # If this node's value has changed, force the needsCalculation
                # flag in the child node...
                if calculate_children == GraphNode.CalculateChildrenType.CALCULATE_CHILDREN:
                    child_node._needsCalculation = True

                # We tell the child node that this parent has calculated...
                child_node.validate()

    def reset_dependencies(self):
        """
        Asks node to recreate its dependencies on other nodes and data objects.
        """
        # We need to know if any new parents have been added to this node
        # by this reset-dependencies operation. So we note the collection
        # before and after setting them up...
        parents_before_reset = self._parents.copy()

        # We remove any existing parents, and add the new ones...
        self.remove_parents()
        self.set_dependencies()

        # We find the collection of nodes that are now parents, but which
        # weren't before, and we tell the graph-manager about them. (This
        # is used to ensure that nodes are correctly calculated if the graph
        # changes shape during the calculation-cycle.)
        new_parents = self._parents.difference(parents_before_reset)
        self.graph_manager.parents_updated(self, new_parents)

    def parent_updated(self, parent):
        """
        Returns true if the node passed in caused the calculation of the calling
        node in this calculation cycle.
        """
        return parent in self._updated_parent_nodes

    def set_gc_type(self, gc_type):
        """
        Sets whether or not this node can be garbage-collected.
        """
        self._gc_type = gc_type
        self.graph_manager.update_gc_info_for_node(self)

    def needs_calculation(self):
        """
        Marks the node as needing calculation in the next calculation cycle.
        """
        self.graph_manager.needs_calculation(self)

    def add_updated_parent(self, node):
        """
        Adds a node to the collection of parent nodes that have updated for the next
        calculation.
        (See the wiki section about "Handling graph shape-changes during calculation"
        for more details.)
        """
        self._updated_parent_nodes.add(node)
        self.graph_manager.node_has_updated_parents(self)

    def clear_updated_parents(self):
        """
        Clears out the collection of updated parents.
        """
        self._updated_parent_nodes.clear()

    def add_gc_ref_count(self):
        """
        Increases the GC ref-count.
        """
        self._gc_ref_count += 1

    def release_gc_ref_count(self):
        """
        Decreases the GC ref count.
        """
        self._gc_ref_count -= 1

    def get_gc_ref_count(self):
        """
        Return the GC ref count.
        """
        return self._gc_ref_count

