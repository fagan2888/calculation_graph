from .quality import Quality


class NodeInfo(object):
    """
    Holds information about one node in the graph.

    The dump() method on GraphManager returns a list of these objects, holding
    one for each node in the graph.
    """
    def __init__(self):
        """
        The 'constructor'.
        """
        # The ID of the node...
        self.node_id = ""

        # The type (class name) of the node...
        self.node_type = ""

        # The quality of the node...
        self.quality = Quality.BAD

        # A text description of the node...
        self.message = ""

        # The set of parent IDs...
        self.parent_ids = set()

