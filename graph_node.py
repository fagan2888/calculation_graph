
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
        self._calcChildren = set()

        # The number of parent nodes which have caused this node to calculate during
        # one calculation cycle...
        self._invalidCount = 0

        # True if this node is marked for calculation in the next cycle...
        self._needsCalculation = True

        # The set of parent nodes that caused this node to calculate in
        # the current calculation cycle...
        self._updatedParentNodes = set()

        # Garbage collection...
        self._gcType = GraphNode.GCType.COLLECTABLE
        self._gcRefCount = 0

    def cleanup(self):
        """
        Cleans up the node and calls dispose() on derived classes.
        """
        self.removeParents()
        self.removeChildren()
        self.dispose()

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
        node._children.remove(this)

        # We mark the graph as needing garbage collection, as removing
        # the parent link may leave unreferenced nodes...
        self._graphManager.linkRemoved()

/****************************************************************************
 removeParents
 -------------
 Removes all parent nodes for this node, also updates the child lists of the
 parents.
****************************************************************************/
void GraphNode::removeParents()
{
	while (!m_parents.empty())
	{
		GraphNode* node = *m_parents.begin()

		m_parents.erase(node)
		node->m_children.erase(this)
	}

	# We mark the graph as needing garbage collection, as removing
	# the parents may leave unreferenced nodes...
	m_graphManager.linkRemoved()
}

/****************************************************************************
 removeChildren
 --------------
 Removes all child nodes for this node, also updates the parent lists of the
 children.
****************************************************************************/
void GraphNode::removeChildren()
{
	while (!m_children.empty())
	{
		GraphNode* node = *m_children.begin()

		m_children.erase(node)
		node->m_parents.erase(this)
	}
}


/****************************************************************************
 hasChildren
 -----------
 Used to determine if this node has any dependents.
****************************************************************************/
bool GraphNode::hasChildren() const
{
	return !m_children.empty()
}

/****************************************************************************
 invalidate
 ----------
 Marks this node as invalid and, if this is the first invalidation, mark all
 direct child nodes as invalid.

 The parent node that is marking this node as needing calculation is passed
 in, so that nodes can see who triggered them to calculate.
****************************************************************************/
void GraphNode::invalidate(GraphNode* pParent)
{
	# We add the parent to the collection of nodes that caused us to
	# recalculate. (If this is one of the 'root' changed nodes for this
	# calculation, the parent will be NULL, so we don't include it.)
	if(pParent != NULL)
	{
		addUpdatedParent(pParent)
	}

	if (!m_invalidCount++)
	{
		# We have just gone invalid, so...
		NodeSet::const_iterator iter

		# Capture child set, as this may change as a result of calculation
		m_calcChildren = m_children

		# Make recursive call for each node in captured child set
		for (iter = m_calcChildren.begin() iter != m_calcChildren.end() ++iter)
		{
			(*iter)->invalidate(this)
		}
	}
}

/****************************************************************************
 validate
 --------
 Reverse a single invalidation of this node and, if no invalidations remain,
 recalculate the node and reverse this nodes invalidation of its direct child
 nodes.
****************************************************************************/
void GraphNode::validate()
{
	if (m_invalidCount <= 0)
	{
		# Something has gone badly wrong in invalidate/validate
		category.error(m_strID + ": Invalidation count is unexpectedly non-positive")
		return
	}

	if (!--m_invalidCount)
	{
		# All our parents are now valid, so we calculate our
		# output value if necessary...
		CalculateChildrenType calculateChildren = DO_NOT_CALCULATE_CHILDREN
		if (m_needsCalculation)
		{
			calculateChildren = calculate()
			m_needsCalculation = false

			# We tell the graph-manager that the node has
			# been calculated...
			m_graphManager.nodeCalculated(this)
		}

		# We calculate our child nodes...
		NodeSet::const_iterator iter
		for (iter = m_calcChildren.begin() iter != m_calcChildren.end() ++iter)
		{
			GraphNode* pChildNode = *iter

			# If this node's value has changed, force the needsCalculation
			# flag in the child node...
			if(calculateChildren == CALCULATE_CHILDREN)
			{
				pChildNode->m_needsCalculation = true
			}

			# Make recursive call to validate for the child node
			pChildNode->validate()
		}
	}
}

/****************************************************************************
 resetDependencies
 -----------------
 Asks node to recreate its dependencies on other nodes and data objects...
****************************************************************************/
void GraphNode::resetDependencies()
{
	# We need to know if any new parents have been added to this node
	# by this reset-dependencies operation. So we note the collection
	# before and after setting them up...
	NodeSet parentsBeforeReset = m_parents

	# We remove any existing parents, and add the new ones...
	removeParents()
	setDependencies()

	# We find the collection of nodes that are now parents, but which
	# weren't before, and we tell the graph-manager about them. (This
	# is used to ensure that nodes are correctly calculated if the graph
	# changes shape during the calculation-cycle.)
	NodeSet newParents
	std::set_difference(m_parents.begin(), m_parents.end(), parentsBeforeReset.begin(), parentsBeforeReset.end(), std::inserter(newParents, newParents.end()))
	m_graphManager.parentsUpdated(this, newParents)
}



/*===========================================================================
 parentUpdated
 -------------
 Returns true if the node passed in caused the calculation of the calling
 node in this calculation cycle.
===========================================================================*/
bool GraphNode::parentUpdated(const GraphNode* pParent) const
{
	return m_updatedParentNodes.find(pParent) != m_updatedParentNodes.end()
}


/*===========================================================================
 setGCType
 ---------
 Sets whether or not this node can be garbage-collected.
===========================================================================*/
void GraphNode::setGCType(GCType gcType)
{
	m_gcType = gcType
	m_graphManager.updateGCInfoForNode(this)
}

/*=============================================================================
 needsCalculation
 ----------------
 Marks the node as needing calculation in the next calculation cycle.
=============================================================================*/
void GraphNode::needsCalculation()
{
	m_graphManager.needsCalculation(this)
}


/*==============================================================================
 addUpdatedParent
 ----------------
 Adds a node to the collection of parent nodes that have updated for the next
 calculation.
 (See the heading comment in GraphManager.cpp about "Handling graph shape-changes
 during calculation" for more details.)
==============================================================================*/
void GraphNode::addUpdatedParent(GraphNode* node)
{
	m_updatedParentNodes.insert(node)
	m_graphManager.nodeHasUpdatedParents(this)
}

/*==============================================================================
 clearUpdatedParents
 -------------------
 Clears out the collection of updated parents.
==============================================================================*/
void GraphNode::clearUpdatedParents()
{
	m_updatedParentNodes.clear()
}

/* static */ GraphDump::Node::StatusType dsc::GraphNode::getNodeStatus(const dsc::Quality& quality)
{
	switch (quality.getEnum())
	{
	case Quality::BAD:
		return GraphDump::Node::ST_BAD
	case Quality::INFO:
		return GraphDump::Node::ST_INFO
	case Quality::GOOD:
		return GraphDump::Node::ST_GOOD
	default:
		break
	}
	return GraphDump::Node::ST_INVALID
}


