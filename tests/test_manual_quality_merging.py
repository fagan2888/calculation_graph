from graph import *


class SourceNode(GraphNode):
    """
    A data source. Just a value with data-quality.
    """
    def __init__(self, source_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_name = source_name

        # The value provided by this source...
        self.value = 0.0

        # True if the source is working correctly...
        self.source_is_good = False

    def set_value(self, value, source_is_good):
        """
        Sets the value of this source and whether the source is good.
        This causes the node to need recalculation.
        """
        self.value = value
        self.source_is_good = source_is_good
        self.needs_calculation()

    def calculate(self):
        """
        We set the data-quality from the source_is_good information.
        """
        self.quality.clear_to_good()
        if self.source_is_good is False:
            self.quality.merge(Quality.BAD, "Source " + self.source_name + " is bad")

        return GraphNode.CalculateChildrenType.CALCULATE_CHILDREN


class SourceChooserNode(GraphNode):
    """
    Chooses between two of the SourceNodes above, depending on
    their data-quality.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Parent nodes...
        self.source_A_node = None
        self.source_B_node = None

        # The value for this node will be chosen from one of the
        # parent sources...
        self.value = 0.0

    def set_dependencies(self):
        """
        We hook up to two sources.
        """
        self.source_A_node = self.add_parent_node(SourceNode, "A")
        self.source_B_node = self.add_parent_node(SourceNode, "B")

    def calculate_quality(self):
        """
        We override automatic quality merging. In this case, we will
        set this node's data-quality in the calculate() function.
        """
        pass

    def calculate(self):
        """
        We choose the value from whichever parent node has Good
        data-quality.
        """
        if self.source_A_node.quality.is_good():
            # Source A has good data...
            self.value = self.source_A_node.value
            self.quality.set_from(self.source_A_node.quality)
        elif self.source_B_node.quality.is_good():
            # Source B has good data...
            self.value = self.source_B_node.value
            self.quality.set_from(self.source_B_node.quality)
        else:
            # Neither source has good data...
            self.value = 0.0
            self.quality.set_to_bad("No source has Good data")

        return GraphNode.CalculateChildrenType.CALCULATE_CHILDREN


def test_manual_quality_merging():
    """
    Tests manual merging of quality from parent nodes.

    The graph for this test has a "redundant" data source. The test node
    has two parents A and B. It chooses which ever one of them has good
    quality.

    So in this case, we do not want to automatically merge quality, as
    otherwise if one of the parents goes Bad, the "choosing" node would
    go bad as well. In this case, as long as one of the parents is Good,
    then the choosing node will be Good as well.
    """
    graph_manager = GraphManager()

    # We create the sources before the chooser, so we can set their values...
    source_A_node = NodeFactory.get_node(graph_manager, GraphNode.GCType.NON_COLLECTABLE, SourceNode, "A")
    source_B_node = NodeFactory.get_node(graph_manager, GraphNode.GCType.NON_COLLECTABLE, SourceNode, "B")

    # We create a node to choose between the two sources above...
    chooser_node = NodeFactory.get_node(graph_manager, GraphNode.GCType.NON_COLLECTABLE, SourceChooserNode)

    # We set both sources to have Good data-quality. The value from source A
    # is chosen when both are good...
    source_A_node.set_value(123.0, source_is_good=True)
    source_B_node.set_value(456.0, source_is_good=True)
    graph_manager.calculate()
    assert chooser_node.value == 123.0
    assert chooser_node.quality.is_good()
    assert chooser_node.quality.get_description() == ""

    # We set source B bad. The value from A should still be used...
    source_B_node.set_value(457.0, source_is_good=False)
    graph_manager.calculate()
    assert chooser_node.value == 123.0
    assert chooser_node.quality.is_good()
    assert chooser_node.quality.get_description() == ""

    # We set source A bad as well...
    source_A_node.set_value(124.0, source_is_good=False)
    graph_manager.calculate()
    assert chooser_node.value == 0.0
    assert chooser_node.quality.is_good() is False
    assert "No source has Good data" in chooser_node.quality.get_description()

    # We set source B Good...
    source_B_node.set_value(567.0, source_is_good=True)
    graph_manager.calculate()
    assert chooser_node.value == 567.0
    assert chooser_node.quality.is_good() is True
    assert chooser_node.quality.get_description() == ""

    # We set source A Good...
    source_A_node.set_value(321.0, source_is_good=True)
    graph_manager.calculate()
    assert chooser_node.value == 321.0
    assert chooser_node.quality.is_good() is True
    assert chooser_node.quality.get_description() == ""

    # We update A...
    source_A_node.set_value(432.0, source_is_good=True)
    graph_manager.calculate()
    assert chooser_node.value == 432.0
    assert chooser_node.quality.is_good() is True
    assert chooser_node.quality.get_description() == ""



