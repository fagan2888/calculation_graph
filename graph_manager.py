from .graph_exception import GraphException


class GraphManager(object):
    """
    The GraphManager manages a 'directed acyclic graph' of nodes and recalculates
    them efficiently as the inputs to those nodes changes.

    See the project's website for full details: http://richard-shepherd.github.io/calculation_graph/

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
    def __init__(self):
        """
        The 'constructor'.
        """
        # The collection of nodes, keyed by ID...
        self._nodes = {}

        # The collection of non-collectable nodes, keyed by ID. These will
        # not be GC'd even if there are no links to them...
        self._non_collectable_nodes = {}

        # The collection of nodes that have changed since the last calculation
        # cycle, keyed by ID...
        self._changed_nodes = {}

        # True if links have changed, and GC may be required
        self._gc_required = False

        # True if we are in the calculate cycle...
        self._is_calculating = False

    def dispose(self):
        """
        The 'destructor'.
        """
        self.delete_nodes()

    def delete_nodes(self):
        """
         We dispose all the nodes and we remove them from the dictionary.
        """
        for key, value in self._nodes:
            value.dispose()

        self._nodes.clear()
        self._non_collectable_nodes.clear()
        self._changed_nodes.clear()

    def add_node(self, node):
        """
        Adds a node to the graph.
        """
        if self.has_node(node.id):
            throw Exception("Node %s already exists", nodeID.c_str());
        else
        {
            m_nodes[nodeID] = node;
            needsCalculation(node);
            m_newNodeIDs.insert(node->getID());
        }
/****************************************************************************
 addNode
 -------
****************************************************************************/
void GraphManager::addNode(GraphNode* node)
{
	const std::string& nodeID = node->getID();

	if (hasNode(nodeID))
	{
		throw Exception("Node %s already exists", nodeID.c_str());
	}
	else
	{
		m_nodes[nodeID] = node;
		needsCalculation(node);
		m_newNodeIDs.insert(node->getID());
	}
}

/*===========================================================================
 deleteNode
 ----------
===========================================================================*/
void GraphManager::deleteNode(GraphNode* node)
{
	if(node != NULL)
	{
		deleteNode(node->getID());
	}
}

/****************************************************************************
 deleteNode
 ----------
****************************************************************************/
void GraphManager::deleteNode(const std::string& id)
{
	NodeMap::iterator it = m_nodes.find(id);
	if(it == m_nodes.end())
	{
		// The node isn't in the graph...
		return;
	}

	GraphNode* pNode = it->second;
	if(m_gcEnabled == true)
	{
		std::string message = Utility::format("You cannot delete nodes in a graph using GC. (Node being deleted, id=%s.)", id.c_str());
		throw Exception(message);
	}
	else
	{
		// GC is not enabled, so we just remove and delete the node...
		deleteAndRemoveNode(pNode);
	}
}

void GraphManager::releaseNode(GraphNode* node)
{
	// You are allowed to release a NULL node. It's just a "no-op"...
	if(node == NULL)
	{
		return;
	}

	// You can only release nodes if GC is being used...
	if(m_gcEnabled == false)
	{
		throw Exception("You cannot release a node with GC disbaled in the GraphManager.");
	}

	// We decrease the ref-count, and see if we can mark the node as
	// needing collection...
	node->releaseGCRefCount();
	int refCount = node->getGCRefCount();
	if(refCount < 0)
	{
		std::string message = Utility::format("Node %s has ref-count < 0.", node->getID().c_str());
		throw Exception(message);
	}

	if(refCount == 0)
	{
		// The node has no references to it, so we mark it as collectable
		// and set the flag so that a GC cycle will take place...
		node->setGCType(GraphNode::COLLECTABLE);
		m_gcRequired = true;
	}
}


/****************************************************************************
 getNode
 -------
****************************************************************************/
GraphNode* GraphManager::getNode(const std::string& id) const
{
	NodeMap::const_iterator iter = m_nodes.find(id);

	if (iter != m_nodes.end())
	{
		return (*iter).second;
	}
	else
	{
		throw Exception("No such node " + id);
	}
}

/****************************************************************************
 hasNode
 -------
****************************************************************************/
bool GraphManager::hasNode(const std::string& id) const
{
	NodeMap::const_iterator it = m_nodes.find(id);
	return it != m_nodes.end() && it->second != NULL;
}

/****************************************************************************
 hasNode
 -------
 This tries to fild the GraphNode using the pointer. It iterates through
 all nodes, so this method can be slow.
****************************************************************************/
bool GraphManager::hasNode(GraphNode * pNode) const
{
    NodeMap::const_iterator it = m_nodes.begin();
    NodeMap::const_iterator itEnd = m_nodes.end();
    for(; it != itEnd; ++it)
    {
        GraphNode* pNode2 = it->second;
        if (pNode == pNode2)
        {
            return true;
        }
    }

    return false;
}

/****************************************************************************
 findNode
 --------
 Returns a pointer to the node identified by 'id' or 0.
****************************************************************************/
GraphNode* GraphManager::findNode(const std::string& id) const
{
	NodeMap::const_iterator it = m_nodes.find(id);
	return it != m_nodes.end() ? it->second : 0;
}

/****************************************************************************
 needsCalculation
 ----------------
 Indicates to the manager that the specified nodes needs (re)calculation.
 This is the only way to indicate that a node requires recalculation.
****************************************************************************/
void GraphManager::needsCalculation(GraphNode* node)
{
	node->m_needsCalculation = true;
	m_changedNodes.insert(node);
}

/****************************************************************************
 calculate
 ---------
 See comments above, and those on 'invalidate' and 'validate' in GraphNode.cpp
****************************************************************************/
void GraphManager::calculate()
{
	// Sets the calculating flag true for the lifetime of this function...
	m_isCalculating = true;

	// We call setDependencies() on any new nodes...
	setDependenciesOnNewNodes();

	// No nodes have been marked as needing calculation, there is nothing to do
	if (m_changedNodes.empty() == false)
	{
		// Take a copy of the nodes requiring calculation
		// New nodes may be added during the calculation process
		NodeSet changedNodes = m_changedNodes;
		NodeSet::const_iterator iter;

		// Clear recalculate list
		m_changedNodes.clear();

		// Invalidate
		for (iter = changedNodes.begin(); iter != changedNodes.end(); ++iter)
		{
			(*iter)->invalidate(NULL);
		}

		// Validate
		for (iter = changedNodes.begin(); iter != changedNodes.end(); ++iter)
		{
			(*iter)->validate();
		}
	}

	// We clear out the collections of updated-parents from any nodes holding them...
	clearUpdatedParents();

	// We clear the collection of new-parents...
	m_mapNewParentsThisCalculationCycle.clear();

	markNodesWithUpdatedLateParents();

	// We garbage collect any unused nodes...
	performGC();

	m_isCalculating = false;
}

/*===========================================================================
 updateGCInfoForNode
 -------------------
 We update our set of non-collectable nodes depending on whether the node
 passed in is collectable or not.
===========================================================================*/
void GraphManager::updateGCInfoForNode(GraphNode* pNode)
{
	if(pNode->m_gcType == GraphNode::NON_COLLECTABLE)
	{
		m_nonCollectableNodes.insert(pNode);
	}
	else
	{
		m_nonCollectableNodes.erase(pNode); // Note: this can be called even if the node is not in the set.
	}
}


/*===========================================================================
 performGC
 ---------
 Cleans up unreferenced nodes if GC is enabled.
===========================================================================*/
void GraphManager::performGC()
{
	if(m_gcEnabled == false || m_gcRequired == false)
	{
		return;
	}
	m_gcRequired = false;

	// To perform GC we start with two collections of nodes:
	// - The set of all nodes in the graph ("all-nodes")
	// - The set of all non-collectable nodes ("non-collectable nodes")
	//
	// For each non-collectable node, we up walk the graph starting with
	// the non-collectable node to find all its parent nodes. Any nodes
	// we find are removed from the all-nodes collection.
	//
	// When we have processed all the non-collectable nodes, any nodes remaining
	// in the all-nodes collection are ones which are not the ancestor of any
	// non-collectable node. They are then all removed from the graph and deleted.

	// We find the set of all nodes in the graph...
	NodeSet allNodes;
	NodeMap::const_iterator itm;
	for(itm=m_nodes.begin(); itm!=m_nodes.end(); ++itm)
	{
		allNodes.insert(itm->second);
	}

	// We remove all ancestors of non-collectable nodes from the set of all-nodes...
	NodeSet::const_iterator it;
	for(it=m_nonCollectableNodes.begin(); it!=m_nonCollectableNodes.end(); ++it)
	{
		GraphNode* node = *it;
		removeParentNodesFromSet(node, allNodes);
	}

	// Any nodes remaining can be deleted...
	NodeSet::const_iterator itd;
	for(itd=allNodes.begin(); itd!=allNodes.end(); ++itd)
	{
		GraphNode* node = *itd;
		deleteAndRemoveNode(node);
	}
}


/*===========================================================================
 removeParentNodesFromSet
 ------------------------
 Removes the node passed in and all its parent nodes from the node-set
 passed in. this will recursively remove all ancestor nodes of the node
 from the set.
===========================================================================*/
void GraphManager::removeParentNodesFromSet(GraphNode* node, NodeSet& nodes)
{
	// We erase the node itself...
	nodes.erase(node);

	// We loop through the parents of the node, erasing them...
	const NodeSet& parents = node->m_parents;
	NodeSet::const_iterator it;
	for(it=parents.begin(); it!=parents.end(); ++it)
	{
		GraphNode* parent = *it;
		removeParentNodesFromSet(parent, nodes);
	}
}

/*===========================================================================
 deleteAndRemoveNode
 -------------------
 Removes the node passed in from the graph and deletes it.
===========================================================================*/
void GraphManager::deleteAndRemoveNode(GraphNode* node)
{
	const std::string& id = node->getID();
	m_nodes.erase(id);
	m_changedNodes.erase(node);
	m_nonCollectableNodes.erase(node);
	m_nodesWithUpdatedParents.erase(node);
	delete node;
}


/*===========================================================================
 setDependenciesOnNewNodes
 -------------------------
 Calls setDependencies() on any nodes that have been added since the
 last calculation cycle.
===========================================================================*/
void GraphManager::setDependenciesOnNewNodes()
{
	if(m_newNodeIDs.empty())
	{
		return;
	}

	// We copy the collection of new node IDs, as the act of setting up
	// the dependencies may cause new nodes to be added in a re-entrant way...
	NodeIDSet nodeIDs = m_newNodeIDs;
	m_newNodeIDs.clear();

	NodeIDSet::iterator it;
	for(it=nodeIDs.begin(); it!=nodeIDs.end(); ++it)
	{
		const std::string& nodeID = *it;

		// We check that the node is in the graph. It is possible
		// that is was added and removed before this function got
		// called...
		NodeMap::iterator itm = m_nodes.find(nodeID);
		if(itm != m_nodes.end())
		{
			GraphNode* node = itm->second;
			node->setDependencies();
		}
	}

	// Setting the dependencies may have caused new nodes to be created. If so,
	// they will needs setting up. We call this function recursively to set
	// them up...
	setDependenciesOnNewNodes();
}

void dsc::GraphManager::dump(std::vector<NodeDump>& target)
{
	// Iterate over all the nodes
	for (NodeMap::const_iterator it = m_nodes.begin(); it != m_nodes.end(); ++it)
	{
		const GraphNode* pNode = it->second;
		// Add a node to the target vector
		NodeDump node;
		node.ID = pNode->getID();
		node.Type = typeid(*pNode).name();
		node.Status = pNode->getNodeStatus();
		node.StatusMessage = pNode->getStatusMessage();

		// Add the parents' IDs to the node
		const NodeSet& parents = pNode->m_parents;
		for (NodeSet::const_iterator itP = parents.begin(); itP != parents.end(); ++itP)
		{
			const GraphNode* pParent = *itP;
			node.Parents.insert(pParent->getID());
		}

		// Insert it into the target container
		target.push_back(node);
	}
}


/*==============================================================================
 parentsUpdated
 --------------
 Called by nodes after their dependencies have changes. We are passed the
 collection of new parents.
==============================================================================*/
void GraphManager::parentsUpdated(GraphNode* node, const NodeSet& newParents)
{
	// We store a map of new-parents -> child nodes.
	// (See heading comment for more details.)

	// We only need to store new parents if we are in the
	// calculation cycle...
	if(m_isCalculating == false)
	{
		return;
	}

	// We note that the node passed in was updated by the parents
	// passed in...
	NodeSet::const_iterator it;
	for(it=newParents.begin(); it!=newParents.end(); ++it)
	{
		// We find the collection of child nodes for this
		// new parent and add the child node to it...
		GraphNode* pParent = *it;
		m_mapNewParentsThisCalculationCycle[pParent].insert(node);
	}
}

/*==============================================================================
 nodeCalculated
 --------------
 Called when a node is calculated.
==============================================================================*/
void GraphManager::nodeCalculated(GraphNode* node)
{
	// We check if the node is a 'late-parent'.
	// (See heading comment for details.)
	MapNewParents::iterator it = m_mapNewParentsThisCalculationCycle.find(node);
	if(it == m_mapNewParentsThisCalculationCycle.end())
	{
		// This node has not been added as a parent to any other
		// nodes (yet) in this calculation cycle...
		return;
	}

	// The node has been added as a parent to other nodes, but it has been
	// calculated after them. So it is a 'late-parent'. We find the
	// collection of child nodes that should have been triggered already
	// and note that they need to be calculated in the next cycle...
	NodeSet& childNodes = it->second;
	m_nodesWithUpdatedLateParents[node] = childNodes;
}

/*==============================================================================
 markNodesWithUpdatedLateParents
 -------------------------------
 Deferred action from above: any nodes for which there is a "late parent"
 (see header comments) are marked for calculation and notified that the
 relevant parent has changed.
==============================================================================*/
void GraphManager::markNodesWithUpdatedLateParents()
{
	for (MapNewParents::iterator it = m_nodesWithUpdatedLateParents.begin(); it != m_nodesWithUpdatedLateParents.end(); ++it)
	{
		GraphNode* pParent = it->first;
		NodeSet& children = it->second;

		// Mark the child nodes as needing calculation, and as triggered by the parent
		for (NodeSet::iterator itChildren = children.begin(); itChildren != children.end(); ++itChildren)
		{
			GraphNode* pChild = *itChildren;

			needsCalculation(pChild);
			pChild->addUpdatedParent(pParent);
		}
	}
	m_nodesWithUpdatedLateParents.clear();
}

/*==============================================================================
 nodeHasUpdatedParents
 ---------------------
 Called when a updated-parent is added to a node. These need to be cleared out
 at the end of the calculation cycle.
==============================================================================*/
void GraphManager::nodeHasUpdatedParents(GraphNode* pNode)
{
	m_nodesWithUpdatedParents.insert(pNode);
}

/*==============================================================================
 clearUpdatedParents
 -------------------
 Clears the collection of updated-parents from all nodes which hold one.
==============================================================================*/
void GraphManager::clearUpdatedParents()
{
	NodeSet::iterator it;
	for(it=m_nodesWithUpdatedParents.begin(); it!=m_nodesWithUpdatedParents.end(); ++it)
	{
		GraphNode* pNode = *it;
		pNode->clearUpdatedParents();
	}
	m_nodesWithUpdatedParents.clear();
}



