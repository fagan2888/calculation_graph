from .graph_exception import GraphException
from .node_info import NodeInfo
from .graph_node import GraphNode


class GraphManager(object):
    """
    The GraphManager manages a 'directed acyclic graph' of nodes and recalculates
    them efficiently as the inputs to those nodes changes.

    See: http:#richard-shepherd.github.io/calculation_graph/GraphManager.html
    """
    def __init__(self):
        """
        The 'constructor'.
        """
        # The collection of nodes, keyed by ID...
        self._nodes = {}

        # The collection of non-collectable nodes, keyed by ID. These will
        # not be GC'd even if there are no links to them...
        self._non_collectable_nodes = set()

        # The collection of nodes that have changed since the last calculation cycle...
        self._changed_nodes = set()

        # Nodes which have a collection of updated-parents. These need to
        # be cleared at the end of the calculation cycle...
        self._nodes_with_updated_parents = set()

        # The collection of IDs of nodes that have been added since the last
        # calculation cycle...
        self._new_node_ids = set()

        # A dictionary of (new parent node) -> (set of child nodes).
        # New parents are parents that have been added to nodes during this calculation cycle.
        self._new_parents_this_calculation_cycle = {}

        # A dictionary of (new parent node) -> (set of child nodes).
        # If one of the above nodes is calculated after it is added as a parent,
        # in the same calculation cycle, then we need to notify the relevant
        # children in the next calculation cycle...
        self._nodes_with_updated_late_parents = {}

        # True if links have changed, and GC may be required
        self._gc_required = False

        # True if we are in the calculate cycle...
        self._is_calculating = False

    def dispose(self):
        """
        The 'destructor'.
        """
        self.dispose_nodes()

    def dispose_nodes(self):
        """
         We dispose all the nodes and we remove them from the dictionary.
        """
        for node_id, node in self._nodes:
            node.cleanup()

        self._nodes.clear()
        self._non_collectable_nodes.clear()
        self._changed_nodes.clear()

    def add_node(self, node):
        """
        Adds a node to the graph.
        """
        if self.has_node(node.node_id):
            raise GraphException("GraphNode " + node.node_id + " already exists")
        else:
            self._nodes[node.node_id] = node
            self.needs_calculation(node)
            self._new_node_ids.add(node.node_id)

    def release_node(self, node):
        """
        Removes interest in a node from one client. If the node's ref-count goes to
        zero, the node will be GC'd.
        """
        # You are allowed to release a None node. It's just a "no-op"...
        if(node is None):
            return

        # We decrease the ref-count, and see if we can mark the node as needing collection...
        node.release_gc_ref_count()
        ref_count = node.get_gc_ref_count()
        if ref_count < 0:
            raise GraphException("GraphNode " + node.node_id + " has ref-count < 0")

        if ref_count == 0:
            # The node has no references to it, so we mark it as collectable
            # and set the flag so that a GC cycle will take place...
            node.set_gc_type(GraphNode.GCType.COLLECTABLE)
            self._gc_required = True

    def get_node(self, node_id):
        """
        Returns the node with the ID passed in.
        Throws an exception if the node does not exist in the graph.
        """
        if node_id in self._nodes:
            return self._nodes[node_id]
        else:
            raise GraphException("No such graph-node " + node_id)

    def has_node(self, node_id):
        """
        Returns True if a node is in the graph for the ID passed in, False otherwise.
        """
        if node_id not in self._nodes:
            return False
        if self._nodes[node_id] is None:
            return False
        return True

    def find_node(self, node_id):
        """
        Returns the node for the ID passed in, or None if it is not in the graph.
        """
        if self.has_node(node_id):
            return self._nodes[node_id]
        else:
            return None

    def needs_calculation(self, node):
        """
        Marks the node passed in for (re)calculation.
        """
        node._needs_calculation = True
        self._changed_nodes.add(node)

    def calculate(self):
        """
        Calculates the graph.
        """
        # Sets the calculating flag true for the lifetime of this function...
        self._is_calculating = True

        # We call setDependencies() on any new nodes...
        self._set_dependencies_on_new_nodes()

        # We calculate if some nodes have been marked as needing calculation since
        # the last time we calculated...
        if self._changed_nodes:
            # We take a copy of the nodes requiring calculation, as
            # new nodes may be added during the calculation process...
            changed_nodes = self._changed_nodes.copy()

            # Clear recalculate list...
            self._changed_nodes.clear()

            # Invalidate...
            for node in changed_nodes:
                node.invalidate(None)

            # Validate...
            for node in changed_nodes:
                node.validate()

        # We clear out the collections of updated-parents from any nodes holding them...
        self.clear_updated_parents()

        # We clear the collection of new-parents...
        self._new_parents_this_calculation_cycle.clear()
        self._mark_nodes_with_updated_late_parents()

        # We garbage collect any unused nodes...
        self._perform_gc()

        self._is_calculating = False

    def update_gc_info_for_node(self, node):
        """
        We update our set of non-collectable nodes depending on whether the node
        passed in is collectable or not.
        """
        if node._gc_type == GraphNode.GCType.NON_COLLECTABLE:
            self._non_collectable_nodes.add(node)
        else:
            if node in self._non_collectable_nodes:
                self._non_collectable_nodes.remove(node)

    def _perform_gc(self):
        """
        Cleans up unreferenced nodes.
        """
        if not self._gc_required:
            return
        self._gc_required = False

        # To perform GC we start with two collections of nodes:
        # - The set of all nodes in the graph ("all-nodes")
        # - The set of all non-collectable nodes ("non-collectable nodes")
        #
        # For each non-collectable node, we up walk the graph starting with
        # the non-collectable node to find all its parent nodes. Any nodes
        # we find are removed from the all-nodes collection.
        #
        # When we have processed all the non-collectable nodes, any nodes remaining
        # in the all-nodes collection are ones which are not the ancestor of any
        # non-collectable node. They are then all removed from the graph and deleted.

        # We find the set of all nodes in the graph...
        all_nodes = set(self._nodes.values())

        # We remove all ancestors of non-collectable nodes from the set of all-nodes...
        for node in self._non_collectable_nodes:
            self._remove_parent_nodes_from_set(node, all_nodes)

        # Any nodes remaining can be deleted...
        for node in all_nodes:
            self._dispose_and_remove_node(node)

    def _remove_parent_nodes_from_set(self, node, nodes):
        """
        Removes the node passed in and all its parent nodes from the node-set
        passed in. This will recursively remove all ancestor nodes of the node
        from the set.
        """
        # We remove the node itself...
        if node in nodes:
            nodes.remove(node)

        # We loop through the parents of the node, removing them...
        parents = node.parents
        for parent in parents:
            self._remove_parent_nodes_from_set(parent, nodes)

    def _dispose_and_remove_node(self, node):
        """
        Removes the node passed in from the graph and disposes it.
        """
        if node.node_id in self._nodes:
            del self._nodes[node.node_id]

        if node in self._changed_nodes:
            self._changed_nodes.remove(node)

        if node in self._non_collectable_nodes:
            self._non_collectable_nodes.remove(node)

        if node in self._nodes_with_updated_parents:
            self._nodes_with_updated_parents.remove(node)

        node.cleanup()

    def _set_dependencies_on_new_nodes(self):
        """
        Calls setDependencies() on any nodes that have been added since the
        last calculation cycle.
        """
        if not self._new_node_ids:
            # There are no new nodes...
            return

        # We copy the collection of new node IDs, as the act of setting up
        # the dependencies may cause new nodes to be added in a re-entrant way...
        node_ids = self._new_node_ids.copy()
        self._new_node_ids.clear()

        for node_id in node_ids:
            # We check that the node is in the graph. It is possible
            # that is was added and removed before this function got
            # called...
            if node_id in self._nodes:
                node = self._nodes[node_id]
                node.set_dependencies()

        # Setting the dependencies may have caused new nodes to be created. If so,
        # they will needs setting up. We call this function recursively to set
        # them up...
        self._set_dependencies_on_new_nodes()

    def dump(self):
        """
        Returns a list of NodeInfo objects, one for each node in the graph.
        These hold information about each node which can be used for logging,
        or to show a graphical representation of the graph.
        """
        # We iterate over all the nodes...
        results = []
        for node in self._nodes:
            # We get the info for this node...
            info = NodeInfo()

            # The main node info...
            info.node_id = node.node_id
            info.node_type = node.get_type()
            info.quality = node.quality
            info.message = node.get_info_message()

            # The IDs of the node's parents...
            for parent in node.parents:
                info.parent_ids.add(parent.node_id)

            results.append(info)

        return results

    def parents_updated(self, node, new_parents):
        """
        Called by nodes after their dependencies have changes. We are passed the
        collection of new parents.
        """
        # We store a map of new-parents -> child nodes.

        # We only need to store new parents if we are in the
        # calculation cycle...
        if not self._is_calculating:
            return

        # We note that the node passed in was updated by the parents
        # passed in...
        for parent in new_parents:
            # We find the collection of child nodes for this
            # new parent and add the child node to it...
            if parent not in self._new_parents_this_calculation_cycle:
                self._new_parents_this_calculation_cycle[parent] = set()
            self._new_parents_this_calculation_cycle[parent].add(node)

    def node_calculated(self, node):
        """
        Called when a node is calculated.
        """
        # We check if the node is a 'late-parent'.
        if node not in self._new_parents_this_calculation_cycle:
            # This node has not been added as a parent to any other
            # nodes (yet) in this calculation cycle...
            return

        # The node has been added as a parent to other nodes, but it has been
        # calculated after them. So it is a 'late-parent'. We find the
        # collection of child nodes that should have been triggered already
        # and note that they need to be calculated in the next cycle...
        child_nodes = self._new_parents_this_calculation_cycle[node]
        self._nodes_with_updated_late_parents[node] = child_nodes

    def _mark_nodes_with_updated_late_parents(self):
        """
        Deferred action from above: any nodes for which there is a "late parent"
        (see header comments) are marked for calculation and notified that the
        relevant parent has changed.
        """
        for parent, children in self._nodes_with_updated_late_parents:
            # Mark the child nodes as needing calculation, and as triggered by the parent...
            for child in children:
                self.needs_calculation(child)
                child.add_updated_parent(parent)
        self._nodes_with_updated_late_parents.clear()

    def node_has_updated_parents(self, node):
        """
        Called when a updated-parent is added to a node. These need to be cleared out
        at the end of the calculation cycle.
        """
        self._nodes_with_updated_parents.add(node)

    def clear_updated_parents(self):
        """
        Clears the collection of updated-parents from all nodes which hold one.
        """
        for node in self._nodes_with_updated_parents:
            node.clear_updated_parents()
        self._nodes_with_updated_parents.clear()

    def get_node_count(self):
        """
        Return the number of nodes in the graph.
        """
        return len(self._nodes)

    def link_removed(self):
        """
        Called by a node to tell the graph that it has removed
        (unlinked) a parent link...
        """
        self._gc_required = True


