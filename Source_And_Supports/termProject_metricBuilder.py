#termProject-Metric_Builder.py
#This section is where I build certain metrics on the network

#imports

import numpy as np
import math
import copy
import classScript #only for test cases

#building data structure of the network

#build helpers

def addEdgeToMatrix(edge,matrix): #helper for buildAdjacencyMatrix
    #get rows and coloumns from ordering of the nodes
    row = edge.toNode.charDict["ordering"]
    col = edge.fromNode.charDict["ordering"]
    if (row == col): #self-edge
        matrix[row][col] = edge.weight*2 #counts both self-edge ends
    else:
        matrix[row][col] = edge.weight
        if (edge.edgeType == "undirected"): #symmetric case
            matrix[col][row] = edge.weight

#actual build

def buildAdjacencyMatrix(graph):
    nodeCounter = 0 #for assigning an order
    #order our nodes
    for node in graph.nodeSet:
        node.charDict["ordering"] = nodeCounter
        nodeCounter += 1
    #prepare adjacency matrix
    pyArray = [[0 for i in xrange(nodeCounter)] for j in xrange(nodeCounter)]
    adjMatrix = np.array(pyArray,dtype = int)
    #populate adjacency matrix with numerical representations of edges
    for edge in graph.edgeSet:
        addEdgeToMatrix(edge,adjMatrix)
    return adjMatrix

#helpers for metric  builders

def normalizeVec(vec): #assists in normalizing a given row vector 
    vecMag = 0.0
    #get magnitude of vector
    for component in vec:
        vecMag += component**2
    vecMag = math.sqrt(vecMag)
    if vecMag == 0.0: #vector has no magnitude, can't be normalized further
        return vec
    else: #make normalization
        for componentInd in xrange(len(vec)):
            vec[componentInd] /= float(vecMag)
        return vec

def isUndirected(adjMatrix): #checks if adjacency matrix of graph is
    #undirected
    for row in xrange(len(adjMatrix)):
        for col in xrange(row+1,len(adjMatrix[0])):
            #if symmetry does not occur across the diagonal, it is not
            #undirected
            if (adjMatrix[row][col] != adjMatrix[col][row]): return False
    #went throught entirely and didn't find a lack of diagonal symmetry
    return True

def findNodesWithDistD(distArray,d): #find nodes with distance d in a 
    #distance array
    distDList = []
    for nodeInd in xrange(len(distArray)):
        if (distArray[nodeInd] == d): distDList.append(nodeInd)
    return distDList

def findOutNeighbors(adjMatrix,nodeInd): #finds out neighbors of a given node
    outNeighborIndList = []
    for row in xrange(len(adjMatrix)):
        if adjMatrix[row][nodeInd] > 0: #there is a connection from node
            #nodeInd to node row
            outNeighborIndList.append(row)
    return outNeighborIndList

#metric builders

def findEigenvectorCentrality(adjMatrix): #finds eigenvector centrality
    (eigVals,eigVectors) = np.linalg.eig(adjMatrix)
    #get leading eigenvalue and leading index of this eigenvalue
    leadingInd = eigVals.argmax()
    leadingEigVec = eigVectors[...,leadingInd]
    return leadingEigVec

def findKatzCentrality(adjMatrix,trials): #finds Katz centrality
    #idea behind this is outlined in Networks, An Introduction pp. 172-175
    #concept: Inverting matrices gets extremely innefficient, hence we want to
    #find Katz centrality through a given number of trials'
    #first, assume a bad estimate on centrality
    KatzCentral = np.matrix([[0] for i in xrange(adjMatrix.shape[0])])
    epsilon = 10**-8 #gives our accuracy for calculating alpha
    leadingEigVal = max(np.linalg.eig(adjMatrix)[0]) #first index has the
    #eigenvalues
    if (leadingEigVal < epsilon): #almost zero
        alpha = 0
    else:
        alpha = (1/leadingEigVal) - epsilon #epsilon prevents divergence
    betaVector = np.matrix([[1] for i in xrange(adjMatrix.shape[0])])
    tempAdjMatrix = np.matrix(adjMatrix) #convert to matrix for now
    for i in xrange(trials):
        KatzCentral = alpha * tempAdjMatrix * KatzCentral + betaVector
    KatzCentral = np.array(KatzCentral,dtype=float).flatten() #flattened vector
    KatzCentral = normalizeVec(KatzCentral)
    return KatzCentral

def calcLocalClusteringCoeffsUndir(adjMatrix): #calculates local clustering
    #coefficients for undirected graphs
    clusterCoeffVec = []
    for row in xrange(len(adjMatrix)):
        neighborsOfI = []
        for col in xrange(len(adjMatrix[row])):
            if (adjMatrix[row,col] > 0): #i is adjacent to j (col)
                neighborsOfI.append(col)
        #numOfPairs is equivalent to \binom{neighbors of i}{2}, i.e. the number
        #of possible adjacencies among neighbors for node i
        numOfPairs = ((float(1)/2) * 
                     (len(neighborsOfI)) * (len(neighborsOfI) - 1))
        #get the number of actual adjacencies among neighbors of node i
        numConnectedPairs = 0 
        for firstNodeInd in xrange(len(neighborsOfI)):
            for secondNodeInd in xrange(firstNodeInd+1,len(neighborsOfI)):
                (firstNode,secondNode) = (neighborsOfI[firstNodeInd],
                                          neighborsOfI[secondNodeInd])
                if (adjMatrix[firstNode,secondNode] > 0): #two neighbors are
                    #adjacent
                    numConnectedPairs += 1
        localClusterCoeff = (float(numConnectedPairs)/numOfPairs if 
                             numOfPairs != 0 else 0 )
        clusterCoeffVec.append(localClusterCoeff)
    #turn into numpy array
    clusterCoeffVec = np.array(clusterCoeffVec,dtype = float)
    return clusterCoeffVec

def calcLocalClusteringCoeffsDir(adjMatrix): #calculates local clustering
###coefficients for directed graphs
    clusterCoeffVec = []
    for col in xrange(len(adjMatrix[0])):
        neighborsOfI = []
        for row in xrange(len(adjMatrix)):
            if (adjMatrix[row,col] > 0): #i is adjacent to j (col)
                neighborsOfI.append(row)
        #numOfPosPairs is equivalent to 2 * \binom{neighbors of i}{2}
        numOfPosPairs = (len(neighborsOfI)) * (len(neighborsOfI) - 1)
        #get number of actual adjacencies among neighbors of node i
        numConnectedPairs = 0
        #note that we go over pairs twice due to directedness
        for fromNodeInd in xrange(len(neighborsOfI)):
            for toNodeInd in xrange(len(neighborsOfI)):
                (fromNode,toNode) = (neighborsOfI[fromNodeInd],
                                         neighborsOfI[toNodeInd])
                if (adjMatrix[toNode,fromNode] > 0 and toNode != fromNode):
                    numConnectedPairs += 1
        #then calculate local clustering coefficient fo rnode i
        localClusterCoeff = (float(numConnectedPairs)/numOfPosPairs if 
                             numOfPosPairs != 0 else 0 )
        clusterCoeffVec.append(localClusterCoeff)
    clusterCoeffVec = np.array(clusterCoeffVec,dtype = float)
    return clusterCoeffVec

def breadthFirstSearch(adjMatrix,sourceKey): #get distances from a node ordered
    #as sourceKey
    queue = [sourceKey,None] #we will append to this
    readPointerInd = 0
    writePointerInd = 1
    distArray = np.array([-1 for i in xrange(adjMatrix.shape[0])],dtype = int)
    distArray[sourceKey] = 0 #setting our source 0
    while (readPointerInd != writePointerInd): #still have unknown distances
        readElement = queue[readPointerInd]
        readPointerInd += 1
        d = distArray[readElement] #gets our initial distance of the read
        #element
        listOfNeighboringNodes = [] 
        for nodeInd in xrange(len(adjMatrix[readElement])):
            if (adjMatrix[nodeInd][readElement] > 0): #it's a neighbor
                listOfNeighboringNodes.append(nodeInd)
        for nodeInd in listOfNeighboringNodes:
            if (distArray[nodeInd] == -1): #haven't seen it yet
                distArray[nodeInd] = d+1 #assign it some distance
                #look further at the node at nodeInd by putting it in the queue
                queue[writePointerInd] = nodeInd 
                queue.append(None)
                writePointerInd += 1
    return distArray

def modifiedBFS(adjMatrix,sourceKey): #implementation for betweenness
    distArray = np.array([-1 for i in xrange(len(adjMatrix))],dtype=int)
    weightArray = np.array([-1 for i in xrange(len(adjMatrix))],dtype=int)
    distArray[sourceKey] = 0
    weightArray[sourceKey] = 1
    leafList = [] #useful for next part of the betweenness algorithm
    d = 0
    nodesWithDistD = True #for controlling while loop
    while (nodesWithDistD): #stops when no vertices have distance d
        nodesWithDistD = False
        considerList = findNodesWithDistD(distArray,d)
        for nodeInd in considerList:
            nodesWithDistD = True #if considerList is empty, we don't reach
            #here
            consideredWeight = weightArray[nodeInd] #assigned
            inList = [i for i in xrange(len(adjMatrix[nodeInd])) if 
                      adjMatrix[nodeInd][i] > 0] #col is from, row is to
            nodeIsLeaf = True #will change depending on neighbors
            for neighborInd in inList:
                if (distArray[neighborInd] == -1): #establish weight, since
                    #you haven't seen it
                    distArray[neighborInd] = d+1
                    weightArray[neighborInd] = consideredWeight
                    nodeIsLeaf = False
                elif (distArray[neighborInd] == d+1): #add weight to it
                    weightArray[neighborInd] += consideredWeight
                    nodeIsLeaf = False
                elif (d+1 > distArray[neighborInd] >= 0): #already added
                    #all considered weight to it
                    pass
            if (nodeIsLeaf): leafList.append(nodeInd)
        d += 1 #increase d
    return (distArray,weightArray,leafList)

def betweennessCalc(adjMatrix,distArray,weightArray,leafList):
    #calculates betweenness centrality for a node
    #give one as a buffer to all nodes
    betweenCentralArray = np.array([1 for i in xrange(len(weightArray))],
                                    dtype = float)
    for i in xrange(len(betweenCentralArray)):
        if (distArray[i] == -1): #never is reached
            betweenCentralArray[i] -= 1
    seenList = [] #add to this considered nodes
    firstDist = max(distArray)
    for dist in xrange(firstDist,0,-1): #moving down distances
        nodeIndList = [i for i in xrange(len(distArray)) 
                       if distArray[i] == dist]
        for nodeInd in nodeIndList:
            consideredDistance = distArray[nodeInd]
            outNeighborIndList = findOutNeighbors(adjMatrix,nodeInd)
            #check neighbors of this node
            for neighborNodeInd in outNeighborIndList:
                #if this node has not been considered and has a distance just
                #1 greater than the current distance considered, we know that
                #it uses our node at nodeInd for betweenness purposes
                if ((distArray[neighborNodeInd] + 1 == consideredDistance) and 
                    (distArray[neighborNodeInd] != -1) and
                    (neighborNodeInd not in seenList)): #assigned it a distance
                    #add to betweenness centrality for the neighboring node
                    betweenCentralArray[neighborNodeInd] += (
                            betweenCentralArray[nodeInd] * float(
                            weightArray[neighborNodeInd])/weightArray[nodeInd])
        seenList.extend(nodeIndList) #add these to our seen list
    return betweenCentralArray

def betweennessCalcWrapper(adjMatrix): #wrapper for whole calculation of
    #betweenness centrality
    betweennessArray = np.array([0 for i in xrange(len(adjMatrix))],
                                dtype = float)
    for nodeInd in xrange(len(adjMatrix)):
        #perform modified BFS to get weights and distances
        (distArray,weightArray,leafList) = modifiedBFS(adjMatrix,nodeInd)
        #move up the BFS tree to get betweenness centrality given this source
        #node
        subBetweennessArray = betweennessCalc(adjMatrix,distArray,
                                                weightArray,leafList)
        betweennessArray += subBetweennessArray
    return betweennessArray

   
################################################################################

#test functions

###helpers for test functions

def getNode(graph,nodeLabel):
   for node in graph.nodeSet:
       if node.label == nodeLabel:
           return node

def almostEqualMatrices(matrix1,matrix2,epsilon = 1*10**(-4)): 
   #variation of almost equal but for arrays
   if (matrix1.shape != matrix2.shape):
       return False
   else:
       if (len(matrix1.shape) == 1): #one dimension
           for i in xrange(matrix1.shape[0]): #rows
               if (abs(matrix1[i] - matrix2[i]) >= epsilon):
                   return False
       else: #two dimension case
           for i in xrange(matrix1.shape[0]): #rows
               for j in xrange(matrix1.shape[1]): #columns
                   if (abs(matrix1[i][j] - matrix2[i][j]) >= epsilon):
                       return False
       #passed the process, hence, all we can do is return true
       return True

def isUnitVector(vec,epsilon=1*10**-3):
   #test to check if a given vector is a unit vector
   vecMag = 0
   for component in vec:
       vecMag += component**2
   vecMag = math.sqrt(vecMag)
   return (abs(1-vecMag) < epsilon)

def checkGenAdjMatrix(graph,adjMatrix): #designed to check all adjacency matrix
#cases
    assert(type(graph) == classScript.graph)
    assert(type(adjMatrix) == np.ndarray)
    assert(adjMatrix.dtype == int)
    numNodes = len(graph.nodeSet)
    assert(len(adjMatrix) == len(adjMatrix[0]) == numNodes)
    for edge in graph.edgeSet:
        fromNodeOrder = edge.fromNode.charDict["ordering"]
        toNodeOrder = edge.toNode.charDict["ordering"]
        edgeWeight = edge.weight
        if (fromNodeOrder == toNodeOrder): #self-edge
            assert(adjMatrix[toNodeOrder][fromNodeOrder] == edgeWeight*2)
        else:
            assert(adjMatrix[toNodeOrder][fromNodeOrder] == edgeWeight)
            if (edge.edgeType == "undirected"): #check other side
                assert(adjMatrix[fromNodeOrder][toNodeOrder] == edgeWeight)


def buildAdjMatBasicCase(): #very basic case
    a = classScript.graph()
    for i in xrange(3):
        newNode = classScript.node(cx=3,cy=5,r=6,label = i)
        a.add_node_man(newNode)
    for node in a.nodeSet:
        for othNode in a.nodeSet:
            if (not(node is othNode)): #no self-edges
                newEdge = classScript.edge(fromNode = node, toNode = othNode,
                                            edgeType = "undirected",
                                            edgeLabel = "basicCaseEdge",
                                            selected = False,
                                            weight = 1)
                a.add_edge_man(newEdge,node,othNode)
    adjMatrix = buildAdjacencyMatrix(a)
    checkGenAdjMatrix(a,adjMatrix)

def buildAdjMatDirCase(): #very undirected graph
    a = classScript.graph()
    newNode = classScript.node(cx = 1, cy = 2, r = 3, label = 0)
    newerNode = classScript.node(cx = 2, cy = 3, r = 5, label = 1)
    othNode = classScript.node(cx = 2, cy = 5, r = 6, label = 2)
    otherNode = classScript.node(cx= 3, cy = 6, r= 7, label = 3)
    nodeList = [newNode,newerNode,othNode,otherNode]
    for node in nodeList:
        a.add_node_man(node)
    highWeightEdge = classScript.edge(fromNode = newNode, toNode = newerNode,
                            edgeType = "directed",edgeLabel ="bigEdge",
                            selected = False, weight = 5)
    a.add_edge_man(highWeightEdge,newNode,newerNode)
    lowWeightEdge = classScript.edge(fromNode= othNode, toNode = otherNode,
                            edgeType = "directed", edgeLabel ="smallerEdge",
                            selected = False, weight = 2)
    a.add_edge_man(lowWeightEdge,newNode,newerNode)
    adjMatrix = buildAdjacencyMatrix(a)
    checkGenAdjMatrix(a,adjMatrix)

def buildAdjMatEdgeCase(): #case with one element pointing to itself
   a = classScript.graph()
   newNode = classScript.node(cx = 4, cy = 6, r = 4, label = 0)
   a.add_node_man(newNode)
   newEdge = classScript.edge(fromNode = newNode, toNode = newNode,
                                edgeType = "directed",edgeLabel = "selfEdge",
                                selected = False, weight = 1)
   a.add_edge_man(newEdge,newNode,newNode)
   adjMatrix = buildAdjacencyMatrix(a)
   checkGenAdjMatrix(a,adjMatrix)

def buildAdjMatBigCase(): #case with big matrix #NEED BETTER SELF-EDGES
    a = classScript.graph()
    for i in xrange(10):
        newNode = classScript.node(cx=3,cy=4,r=3,label=i)
        newEdge = classScript.edge(fromNode = newNode,toNode = newNode,
                                edgeType = "directed", edgeLabel = "selfEdge",
                                selected = False, weight = 1)
        a.add_node_man(newNode)
        a.add_edge_man(newEdge,newNode,newNode)
    adjMatrix = buildAdjacencyMatrix(a)
    checkGenAdjMatrix(a,adjMatrix)

def testAddEdgeToMatrixDirCase(): #test on the directed edge case
    fromNode = classScript.node(cx=5,cy=3,r=3,label=0)
    fromNode.charDict["ordering"] = 0
    toNode = classScript.node(cx=6,cy=5,r=3,label=1)
    toNode.charDict["ordering"] = 1
    newEdge = classScript.edge(fromNode=fromNode,toNode=toNode,
                    edgeType="directed",edgeLabel="directedCase",selected=True,
                    weight = 1)
    adjMatrix = np.array([[0,0,0],[0,0,0],[0,0,0]],dtype = int)
    addEdgeToMatrix(newEdge,adjMatrix)
    solution = np.array([[0,0,0],[1,0,0],[0,0,0]],dtype = int)
    assert (np.array_equal(solution,adjMatrix))

def testAddEdgeToMatrixUndirCase(): #test on the undirected edge case
    fromNode = classScript.node(cx=5,cy=3,r=3,label=0)
    fromNode.charDict["ordering"] = 0
    toNode = classScript.node(cx=6,cy=5,r=3,label=1)
    toNode.charDict["ordering"] = 2
    newEdge = classScript.edge(fromNode=fromNode,toNode=toNode,
                    edgeType="undirected",edgeLabel="undirectedCase",
                    selected=True,weight = 1)
    adjMatrix = np.array([[0,0,0],[0,0,0],[0,0,0]],dtype = int)
    addEdgeToMatrix(newEdge,adjMatrix)
    solution = np.array([[0,0,1],[0,0,0],[1,0,0]],dtype = int)
    assert(np.array_equal(solution,adjMatrix))

def testAddEdgeToMatrixOverwriteCase(): #test where we overwrite an edge
    fromNode = classScript.node(cx=5,cy=3,r=3,label=0)
    fromNode.charDict["ordering"] = 0
    toNode = classScript.node(cx=6,cy=5,r=3,label=1)
    toNode.charDict["ordering"] = 1
    newEdge = classScript.edge(fromNode=fromNode,toNode=toNode,
                    edgeType="undirected",edgeLabel="undirectedCase",
                    selected=True,weight = 2)
    adjMatrix = np.array([[0,1,0],[1,0,0],[0,0,0]],dtype = int)
    addEdgeToMatrix(newEdge,adjMatrix)
    solution = np.array([[0,2,0],[2,0,0],[0,0,0]],dtype = int)
    assert(np.array_equal(solution,adjMatrix))

def testAddEdgeToMatrixAddedWeightCase(): #test where we have more weight on 
#edge
    fromNode = classScript.node(cx=5,cy=3,r=3,label=0)
    fromNode.charDict["ordering"] = 0
    toNode = classScript.node(cx=6,cy=5,r=3,label=1)
    toNode.charDict["ordering"] = 2
    newEdge = classScript.edge(fromNode=fromNode,toNode=toNode,
                    edgeType="undirected",edgeLabel="undirectedCase",
                    selected=True,weight = 3)
    adjMatrix = np.array([[0,0,0],[0,0,0],[0,0,0]],dtype = int)
    addEdgeToMatrix(newEdge,adjMatrix)
    solution = np.array([[0,0,3],[0,0,0],[3,0,0]],dtype = int)
    assert(np.array_equal(solution,adjMatrix))

def testAddEdgeToMatrixSelfEdgeCase(): #tests self-edge case
    fromNode = classScript.node(cx=5,cy=3,r=3,label=0)
    fromNode.charDict["ordering"] = 0
    newEdge = classScript.edge(fromNode=fromNode,toNode=fromNode,
                    edgeType="undirected",edgeLabel="undirectedCase",
                    selected=True,weight = 1)
    adjMatrix = np.array([[0,0,0],[0,0,0],[0,0,0]],dtype = int)
    addEdgeToMatrix(newEdge,adjMatrix)
    solution = np.array([[2,0,0],[0,0,0],[0,0,0]],dtype = int)
    assert(np.array_equal(solution,adjMatrix))

#actual test functions

def testAddEdgeToMatrix():
    testAddEdgeToMatrixDirCase() #test where we add a directed edge
    testAddEdgeToMatrixUndirCase() #test where we add an undirected edge
    testAddEdgeToMatrixOverwriteCase() #test where we overwrite a part of
    #the matrix
    testAddEdgeToMatrixAddedWeightCase() #case with added weight on edge
    testAddEdgeToMatrixSelfEdgeCase() #case with self-edge
    print "You passed testAddEdgeToMatrix! Have a polar bear."

def testBuildAdjacencyMatrix():
    buildAdjMatBasicCase() #very basic case
    buildAdjMatEdgeCase() #case with one element pointing to itself
    buildAdjMatDirCase() #directed graph
    buildAdjMatBigCase() #case with big matrix and some self-edges
    print "You passed testBuildAdjacencyMatrix! Have a second polar bear."

def testNormalizeVec():
    vec = np.array([1,0,0],dtype = float) #already normalized
    assert(np.array_equal(normalizeVec(vec),np.array([1,0,0],dtype = float)))
    vec = np.array([1,1,1],dtype = float)
    solutionVec = np.array([1/math.sqrt(3),1/math.sqrt(3),1/math.sqrt(3)],
                            dtype = float)
    assert(almostEqualMatrices(normalizeVec(vec),solutionVec))
    vec = np.array([-4,-3,0],dtype= float) #negative values
    solutionVec = np.array([float(-4)/5,float(-3)/5,float(0)/5],dtype = float)
    assert(almostEqualMatrices(normalizeVec(vec),solutionVec))
    vec = np.array([0,0,0],dtype = float) #major edge case, magnitude 0
    solutionVec = vec #because we can't normalize it
    assert(almostEqualMatrices(normalizeVec(vec),solutionVec))
    vec = np.array([1.4,3,4,5,6],dtype = float) #big vector
    vecMag = math.sqrt(1.4**2 + 3**2 + 4**2 + 5**2 + 6**2)
    solutionVec = np.array([1.4/vecMag,3/vecMag,4/vecMag,5/vecMag,6/vecMag],
                            dtype = float)
    assert(almostEqualMatrices(normalizeVec(vec),solutionVec))
    print "You passed testNormalizeVec! Have a third polar bear."

def testIsUndirected():
    adjMatrix = np.array([[0,1,1],[1,0,1],[1,1,0]],dtype = int)#symmetric matrix
    assert(isUndirected(adjMatrix) == True)
    adjMatrix = np.array([[0,1,2],[1,0,1],[1,1,0]],dtype = int) #slight skew
    assert(isUndirected(adjMatrix) == False)
    adjMatrix = np.array([[1]],dtype = int) #small matrix
    assert(isUndirected(adjMatrix) == True)
    adjMatrix = np.array([[0,0],[0,0]],dtype = int) #empty matrix
    assert(isUndirected(adjMatrix) == True)
    adjMatrix = np.array([[0,0,0,0,1],
                        [0,0,0,0,3],
                        [0,3,4,5,7],
                        [0,2,3,5,7],
                        [1,0,0,2,3]],dtype = int) #big, obviously directed case
    assert(isUndirected(adjMatrix) == False)
    print "You passed testIsUndirected! Have a fourth polar bear."

def testFindNodesWithDistD():
    distArray = np.array([0,1,2,0,0,0],dtype = int)
    assert(findNodesWithDistD(distArray,0) == [0,3,4,5])
    distArray = np.array([1,1,1,1],dtype = int) #all the same
    assert(findNodesWithDistD(distArray,1) == [0,1,2,3])
    distArray = np.array([4,23,2,1,5],dtype = int) #case with no seven
    assert(findNodesWithDistD(distArray,7) == [])
    distArray = np.array([3,1.3,1.2,1.1,1.0,1,1.4],dtype = float) #case with
    #close distances
    assert(findNodesWithDistD(distArray,1) == [4,5])
    distArray = np.array([],dtype = int) #case with no values in it
    assert(findNodesWithDistD(distArray,4) == [])
    print "You passed testFindNodesWithDistD! Have a fifth polar bear."

def testFindOutNeighbors():
    adjMatrix = np.array([[0,1,1],[1,0,1],[1,1,0]],dtype = int) #symmetric case
    assert(findOutNeighbors(adjMatrix,0) == [1,2])
    adjMatrix = np.array([[0,0,1],[0,0,1],[0,0,1]], dtype = int) #undir case
    assert(findOutNeighbors(adjMatrix,0) == []) #no out neighbors
    adjMatrix = np.array([[2]], dtype = int) #small case
    assert(findOutNeighbors(adjMatrix,0) == [0])
    adjMatrix = np.array([[0,0,1],[0,2,0],[2,0,0]],dtype = int) #case with
    #added weights on edges
    assert(findOutNeighbors(adjMatrix,2) == [0])
    print "You passed testFindOutNeighbors! Have a sixth polar bear."

def testFindEigenvectorCentrality():
    adjMatrix = np.array([[2,0],[0,2]],dtype = int) #basic symmetric case
    leadingEigVec = np.array([1,0],dtype = float)
    testVec = findEigenvectorCentrality(adjMatrix)
    assert(isUnitVector(testVec))
    assert(almostEqualMatrices(testVec, leadingEigVec))
    adjMatrix = np.array([[0,1,1],[1,0,1],[0,1,1]],dtype = int) #Clique Matrix
    leadingEigVec = np.array([.5773,.5773,.5773], dtype = float)    
    testVec = findEigenvectorCentrality(adjMatrix)
    assert(isUnitVector(testVec))
    assert(almostEqualMatrices(testVec, leadingEigVec))
    adjMatrix = np.array([[0,0,0],[0,0,0],[0,0,0]], dtype = int) #empt edge case
    leadingEigVec = np.array([1,0,0],dtype = float)
    testVec = findEigenvectorCentrality(adjMatrix)
    assert(isUnitVector(testVec))
    assert(almostEqualMatrices(testVec, leadingEigVec))
    print "You passed testFindEigenvectorCentrality! Have a seventh polar bear."

def testFindKatzCentrality(): #TEST THIS ONE MORE
    adjMatrix = np.array([[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]],dtype=int)
    solutionVec = np.array([.5,.5,.5,.5],dtype = float) #outcome of
    #300 trials on each of these vertices
    testVec = findKatzCentrality(adjMatrix,300)
    assert(isUnitVector(testVec))
    assert(almostEqualMatrices(testVec,solutionVec))
    adjMatrix = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]],dtype=int)
    solutionVec = np.array([.5,.5,.5,.5], dtype = float)
    testVec = findKatzCentrality(adjMatrix,1000)
    assert(isUnitVector(testVec))
    assert(almostEqualMatrices(testVec,solutionVec))
    #directed graph, asymmetrical,weighted edges
    adjMatrix = np.array([[0,1,3,4],[0,0,1,1],[7,6,0,3],[7,2,3,0]],dtype =int)
    solutionVec = np.array([.4755,.1327,.6361,.5929],dtype = float)
    testVec = findKatzCentrality(adjMatrix,1000)
    assert(isUnitVector(testVec))
    assert(almostEqualMatrices(testVec,solutionVec))
    print "You passed testFindKatzCentrality! Have a third polar bear."

def testCalcLocalClusteringCoeffsUndir():
    #empty edge case
    adjMatrix = np.array([[0,0,0] for i in xrange(3)], dtype = int)
    solutionVec = np.array([0,0,0],dtype = float)
    testVec = calcLocalClusteringCoeffsUndir(adjMatrix)
    assert(almostEqualMatrices(testVec,solutionVec))
    adjMatrix = np.array([[0,1,1],[1,0,1],[1,1,0]],dtype = int) #clique case
    solutionVec = np.array([1,1,1], dtype = float)
    testVec = calcLocalClusteringCoeffsUndir(adjMatrix)
    assert(almostEqualMatrices(testVec,solutionVec))
    adjMatrix = np.array([[1]], dtype = int)
    solutionVec = np.array([0],dtype = int) #singleton node, so no clustering
    testVec = calcLocalClusteringCoeffsUndir(adjMatrix)
    assert(almostEqualMatrices(testVec,solutionVec))
    adjMatrix = np.array([[0,1,1,1],[1,0,0,1],[1,0,0,0],[1,1,0,0]],dtype = int)
    solutionVec = np.array([float(1)/3,1,0,1],dtype = float)
    testVec = calcLocalClusteringCoeffsUndir(adjMatrix)
    assert(almostEqualMatrices(testVec,solutionVec))
    print "You passed testCalcLocalClusteringCoeffsUndir! Have a ninth" \
    " polar bear."

def testCalcLocalClusteringCoeffsDir():
    adjMatrix = np.array([[0,0,0] for i in xrange(3)], dtype = int)
    solutionVec = np.array([0,0,0],dtype = float)
    testVec = calcLocalClusteringCoeffsDir(adjMatrix)
    assert(almostEqualMatrices(testVec,solutionVec))
    adjMatrix = np.array([[0,0,0],[1,0,1],[1,0,0]],dtype = int) #small directed
    #case
    solutionVec = np.array([.5,0,0], dtype = float)
    testVec = calcLocalClusteringCoeffsDir(adjMatrix)
    assert(almostEqualMatrices(testVec,solutionVec))
    adjMatrix = np.array([[0,1,0],[1,0,1],[1,1,0]],dtype = int) #more edges
    solutionVec = np.array([1,.5,0], dtype = float)
    testVec = calcLocalClusteringCoeffsDir(adjMatrix)
    assert(almostEqualMatrices(testVec,solutionVec))
    adjMatrix = np.array([[1]], dtype = int)
    solutionVec = np.array([0],dtype = int) #singleton node
    testVec = calcLocalClusteringCoeffsUndir(adjMatrix)
    assert(almostEqualMatrices(testVec,solutionVec))
    print "You passed testCalcLocalClusteringCoeffsDir! have a tenth" \
    " polar bear."

def testBreadthFirstSearch():
    #full-clique case
    adjMatrix = np.array([[0,1,1,1],[1,0,1,1],[1,1,0,1],[1,1,1,0]],dtype=int)
    solutionArray = np.array([0,1,1,1],dtype=int)
    assert(np.array_equal(breadthFirstSearch(adjMatrix,0),solutionArray))
    adjMatrix = np.array([[0,0,0],[1,0,0],[0,0,0]],dtype = int) #directed case
    solutionArray = np.array([0,1,-1], dtype = int)
    assert(np.array_equal(breadthFirstSearch(adjMatrix,0),solutionArray))
    solutionArray = np.array([-1,0,-1],dtype = int) #start from 1st source key
    assert(np.array_equal(breadthFirstSearch(adjMatrix,1),solutionArray))
    adjMatrix = np.array([[0,1,1,0,0],[1,0,0,0,1],[1,0,0,1,0],[0,0,1,0,0],
                         [0,1,0,0,0]],dtype = int)
    solutionArray = np.array([0,1,1,2,2], dtype = int) #from key 0
    assert(np.array_equal(breadthFirstSearch(adjMatrix,0),solutionArray))
    solutionArray = np.array([2,1,3,4,0], dtype = int) #from key 3
    assert(np.array_equal(breadthFirstSearch(adjMatrix,4),solutionArray))
    print "You passed testBreadthFirstSearch! Have an eleventh polar bear."

def testModifiedBFS():
    adjMatrix = np.array([[0,1,1,0,0,0,0],[0,0,0,1,0,0,0],[0,0,0,1,1,0,0],
                            [0,0,0,0,0,1,0],[0,0,0,0,0,1,1],[0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0]],dtype = int)
    solutionSet = (np.array([0,1,1,2,2,3,3],dtype=int),np.array([1,1,1,2,1,3,1],
                            dtype = int),[5,6])
    for i in xrange(len(solutionSet)):
        assert(np.array_equal(modifiedBFS(adjMatrix,0)[i],solutionSet[i]))
    adjMatrix = np.array([[1]],dtype = int) #small case
    solutionSet = (np.array([0],dtype=int),np.array([1],dtype=int),[0])
    for i in xrange(len(solutionSet)):
        assert(np.array_equal(modifiedBFS(adjMatrix,0)[i],solutionSet[i]))
    adjMatrix = np.array([[0,1,1,0,0,0,0],[0,0,0,1,0,0,0],[0,0,0,1,1,0,0],
                            [0,0,0,0,0,1,0],[0,0,0,0,0,1,1],[0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0]],dtype = int)
    solutionSet = (np.array([-1,0,-1,1,-1,2,-1],dtype=int), #dif sourceKey
                    np.array([-1,1,-1,1,-1,1,-1],dtype = int),[5])
    for i in xrange(len(solutionSet)):
        assert(np.array_equal(modifiedBFS(adjMatrix,1)[i],solutionSet[i]))
    print "You passed testModifiedBFS! Have a twelfth polar bear."


def testBetweennessCalc():
    #test cases come from Networks, an Introductions pp. 326
    adjMatrix = np.array([[0,1,1,0,0,0,0],[0,0,0,1,0,0,0],[0,0,0,1,1,0,0],
                            [0,0,0,0,0,1,0],[0,0,0,0,0,1,1],[0,0,0,0,0,0,0],
                            [0,0,0,0,0,0,0]],dtype = int)
    (distArray,weightArray,leafList) = modifiedBFS(adjMatrix,0) #key from 0
    solutionVec = np.array([7,float(11)/6,float(25)/6,float(5)/3,float(7)/3,
                            1,1],dtype=float)
    testVec = betweennessCalc(adjMatrix,distArray,weightArray,leafList)
    assert(almostEqualMatrices(testVec,solutionVec))
    adjMatrix = np.array([[0,1,1,0,0,0,0],[0,0,0,1,0,0,0],[0,0,0,0,1,1,0],
                            [0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,1],
                            [0,0,0,0,0,0,0]],dtype = int)
    (distArray,weightArray,leafList) = modifiedBFS(adjMatrix,0) #key from 0
    solutionVec = np.array([7,2,4,1,1,2,1],dtype=float)
    testVec = betweennessCalc(adjMatrix,distArray,weightArray,leafList)
    assert(almostEqualMatrices(testVec,solutionVec))
    print "You passed testBetweennessCalc! Have a thirteenth polar bear."

def testBetweennessCalcWrapper():
    adjMatrix = np.array([[0,1,1],[1,0,1],[1,1,0]],dtype=int)
    solutionVec = np.array([5,5,5],dtype = float)
    assert(np.array_equal(betweennessCalcWrapper(adjMatrix),solutionVec))
    adjMatrix = np.array([[0,1,1],[1,0,0],[1,0,0]],dtype = int) #smaller case
    solutionVec = np.array([7,5,5],dtype = float)
    assert(np.array_equal(betweennessCalcWrapper(adjMatrix),solutionVec))
    adjMatrix = np.array([[0,1,0],[0,0,0],[0,0,0]],dtype = int) #unconnected
    #graph
    solutionVec = np.array([2,2,1],dtype = float)
    assert(np.array_equal(betweennessCalcWrapper(adjMatrix),solutionVec))
    adjMatrix = np.array([[0,1,1,1,1],[1,0,0,0,0],[1,0,0,0,0],[1,0,0,0,0],
                        [1,0,0,0,0]],dtype = int) #star graph
    solutionVec = np.array([21,9,9,9,9],dtype = float)
    assert(np.array_equal(betweennessCalcWrapper(adjMatrix),solutionVec))
    print "You passed testBetweennessCalcWrapper! Have a fourteenth polar bear."

def testAll():
    testAddEdgeToMatrix()
    testBuildAdjacencyMatrix()
    testNormalizeVec()
    testIsUndirected()
    testFindNodesWithDistD()
    testFindOutNeighbors()
    testFindEigenvectorCentrality()
    testFindKatzCentrality()
    testCalcLocalClusteringCoeffsUndir()
    testCalcLocalClusteringCoeffsDir()
    testBreadthFirstSearch()
    testModifiedBFS()
    testBetweennessCalc()
    testBetweennessCalcWrapper()
    print "You passed all the test functions! Have fun with all those" \
    " polar bears."

if __name__ == "__main__":
    testAll()
