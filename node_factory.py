
class NodeFactory(object):
    """
    Static methods for creating / finding nodes, and adding them to the
    graph manager.
    """
    @staticmethod
    def get_node(graph_manager, environment, gc_type, node_type, *args, **kwargs):
        """
        """
        from .graph_node import GraphNode

        # We find the ID of the node. This is made up of the node's type (as a string)
        # plus it's identity parameters...
        node_type_name = node_type.get_type()
        if not node_type_name:
            node_type_name = node_type.__name__
        node_id = node_type_name + "." + node_type.make_id(*args)

        # We check if the node is already in the graph and create it
        ## if it is not...
        node = graph_manager.find_node(node_id)
        if node is None:
            # We create the new node 'manually' so that we can set the
            # graph-manager, environment and ID in the base class without
            # having to pass them to the derived class's constructor...
            node = object.__new__(node_type, *args, **kwargs)
            node.graph_manager = graph_manager
            node.environment = environment
            node.node_id = node_id
            node.__init__(*args, **kwargs)

            # We add the node to the graph...
            graph_manager.add_node(node)

        # We add a ref-count for non-collectable nodes (regardless of whether
        # it is hooked up to other nodes)...
        if gc_type == GraphNode.GCType.NON_COLLECTABLE:
            node.add_gc_ref_count()
            node.set_gc_type(GraphNode.GCType.NON_COLLECTABLE)

        return node

