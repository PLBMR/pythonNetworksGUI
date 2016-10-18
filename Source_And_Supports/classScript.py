#classScript.py
#script dedicated to writing the classes referenced universally in other scripts


#idea for making a universal classScript came from my mentor Evan Bergeron 
#andrew (ebergero)

#things to fix:
#1. NEED TO MAKE ADDING EDGES QUICKER
#2. Need to add better check for legality on edges

from structClass import Struct
import Tkinter as tk #for proper implementation with GUI

class graph(Struct):
    def __init__(self):
        self.nodeSet = set([])
        self.edgeSet = set([])

    #metric build

    def buildMetrics(self):
        import termProject_metricBuilder as mb #put in function in order to 
        #prevent both scripts from recursively importing each other
        adjMatrix = mb.buildAdjacencyMatrix(self)
        eigVec = mb.findEigenvectorCentrality(adjMatrix)
        trials = 400
        katzVec = mb.findKatzCentrality(adjMatrix,trials)
        if (mb.isUndirected(adjMatrix)): #checks if undirected adjacency matrix
            clusterCoeffVec = mb.calcLocalClusteringCoeffsUndir(adjMatrix)
        else:
            clusterCoeffVec = mb.calcLocalClusteringCoeffsDir(adjMatrix)
        betweennessVec = mb.betweennessCalcWrapper(adjMatrix)
        for node in self.nodeSet:
            #index made when building matrix
            nodeMatrixInd = node.charDict["ordering"]
            node.charDict["EigvecCentral"] = eigVec[nodeMatrixInd]
            node.charDict["katzCentral"] = katzVec[nodeMatrixInd]
            node.charDict["localClusterCoeff"] = clusterCoeffVec[nodeMatrixInd]
            node.charDict["BetweenCentral"] = betweennessVec[nodeMatrixInd]

    def performBFS(self,node):
        import termProject_metricBuilder as mb #put in function in order to 
        #prevent both scripts from recursively importing each other
        adjMatrix = mb.buildAdjacencyMatrix(self)
        sourceKey = node.charDict["ordering"] #assigned in adjMatrix
        distVec = mb.breadthFirstSearch(adjMatrix,sourceKey)
        for node in self.nodeSet:
            nodeMatrixInd = node.charDict["ordering"]
            node.charDict["BFS"] = distVec[nodeMatrixInd]

    def add_node(self,nodeCX,nodeCY,nodeR,nodeLabel):
        newNode = node(cx = nodeCX, cy = nodeCY, r = nodeR, label = nodeLabel)
        self.nodeSet.add(newNode) #need to label them
        #numerically for the sake of pointing to correct adjacency list

    def add_node_man(self,node): #for adding node manually
        self.nodeSet.add(node)

    def add_nodes(self,nodeList):
        (cxInd,cyInd,rInd,labelInd) = (0,1,2,3) #need this for pulling info from
        #elements of node list
        if (type(nodeList) == list): #need it to be a list
            for nodeTup in nodeList:
                if (type(nodeTup) == tuple): #need it to be a tuple
                    self.add_node(nodeTup[cxInd],nodeTup[cyInd],nodeTup[rInd],
                        nodeTup[labelInd])

    def removeNode(self,node):
        edgeDeleteList = [] #for deleting edg
        for edge in self.edgeSet:
            if (edge.incidentWith(node)): #incident with given edge
                edgeDeleteList.append(edge)
        for edge in edgeDeleteList:
            self.removeEdge(edge)
        for othNode in self.nodeSet:
            if (othNode.uniqueLabel == node.uniqueLabel):
                consideredNode = othNode
                self.nodeSet.remove(consideredNode)
                break

    def newNodeLabel(self,label): #checks to see if no other nodes have a given
        for node in self.nodeSet:
            if (node.label == label):
                return False
        #if we are here, there are no nodes with that given label
        return True

    def getNode(self,label): #finds a node given a particular label
        for node in self.nodeSet:
            if (node.label == label):
                return node
        #couldn't find node with that given label, return None
        return None

    #clean up times when done

    def add_edge(self,firstNode,secondNode,edgeType,edgeLabel,selected,weight):
        #adds an edge to our graph
        newEdge = edge(fromNode = firstNode,toNode = secondNode,
                        edgeType = edgeType, edgeLabel = edgeLabel,
                        selected=selected,
                        weight = weight)
        if (newEdge.edgeType == "undirected"): #do this two ways
            self.edgeSet.add(newEdge)
            firstNode.outSet.add(secondNode)
            firstNode.inSet.add(secondNode)
            if (firstNode != secondNode):
                secondNode.outSet.add(firstNode)
                secondNode.inSet.add(firstNode)
        else: #directed instance, just one way
            self.edgeSet.add(newEdge)
            firstNode.outSet.add(secondNode)
            secondNode.inSet.add(firstNode)

    def add_edges(self,edgeList):
        #adds several edges to our graph at once
        (fNodeInd,tNodeInd,typeInd,labelInd,weightInd) = (0,1,2,3,4)
        if (type(edgeList) == list): #need it to be a list
            for edgeTup in edgeList:
                if (type(edgeTup) == tuple): #need it to be a tuple
                    self.add_edge(edgeTup[fNodeInd],edgeTup[tNodeInd],
                        edgeTup[typeInd],edgeTup[labelInd],edgeTup[weightInd])

    def add_edge_man(self,edge,firstNode,secondNode):
        #manual addition of edges
        self.edgeSet.add(edge)
        if (edge.edgeType == "undirected"):
            #need to add connection both ways
            firstNode.outSet.add(secondNode)
            firstNode.inSet.add(secondNode)
            if (firstNode != secondNode): #not a self-edge
                secondNode.outSet.add(firstNode)
                secondNode.inSet.add(firstNode)
        else:
            #add edges just one way
            firstNode.outSet.add(secondNode)
            secondNode.inSet.add(firstNode)

    def removeEdge(self,edge):
        #removes an edge from the graph
        if (edge.edgeType == "undirected"):
            #remove both directions
            edge.fromNode.inSet.remove(edge.toNode)
            edge.fromNode.outSet.remove(edge.toNode)
            edge.toNode.inSet.remove(edge.fromNode)
            edge.toNode.outSet.remove(edge.fromNode)
        else: #directed case, just one direction
            edge.fromNode.outSet.remove(edge.toNode)
            edge.toNode.inSet.remove(edge.fromNode)
        self.edgeSet.remove(edge)

    def wikiCleaner(self): #cleans graph after wiki scrape
        for node in self.nodeSet:
            #clean labels
            labelListing = node.label.split("/")
            node.label = labelListing[len(labelListing)-1] #last part is label
            #unselect
            node.selected = False
        for edge in self.edgeSet:
            #clean edge label
            edgeListing = edge.edgeLabel.split(" to ")
            edgeParts = [] #add to this for new label
            for edgePart in edgeListing:
                edgePart = edgePart.split("/")
                edgePart = edgePart[len(edgePart)-1]
                edgeParts.append(edgePart)
            edge.edgeLabel = str(edgeParts[0]) + " to " + str(edgeParts[1])

    #drawing graph

    def draw(self, canvas): #general drawing method for the graph
        for edge in self.edgeSet:
            edge.draw(canvas)
        for node in self.nodeSet:
            node.draw(canvas)

class node(Struct):
    def __init__(self,cx,cy,r,label):
        #centering and radius
        self.cx = cx
        self.cy = cy
        self.r = r
        self.drawMargin = 8 #just for drawing
        self.selected = True
        #sets for adjacencies
        self.outSet = set([])
        self.inSet = set([])
        self.label = label
        self.uniqueLabel = label #distinguished what can be changed and
        #what can't
        self.showInfo = False #for showing info
        self.charDict = {} #for adding additional information
        #what not to display in dashboard information
        self.nondisplayGroup = ["uniqueLabel","selected",
        "showInfo","nondisplayGroup","outSet","inSet"]

    def __eq__(self,other): #difficult decision, but makes uniqueness easier
        return self.uniqueLabel == other.uniqueLabel

    def __repr__(self):
        return str(type(self).__name__) + "(" + str(self.uniqueLabel) + ")"

    #drawing functions

    #draw helpers

    def drawSelectedOval(self,canvas): #drawn if node is selected
        canvas.create_oval(self.cx-(self.r+self.drawMargin),
                                self.cy-(self.r+self.drawMargin),
                               self.cx+(self.r+self.drawMargin),
                               self.cy+(self.r+self.drawMargin),
                               fill = "#FFFF00") #yellow

    def drawOuterOval(self,canvas): #outer oval of node
        canvas.create_oval(self.cx-self.r,self.cy-self.r,
                           self.cx+self.r,self.cy+self.r,
        fill = "#4F759B") #see http://www.color-hex.com/color/4f759b

    def drawInnerOval(self,canvas): #inner oval of node
        canvas.create_oval(self.cx-(self.r-self.drawMargin),
                           self.cy-(self.r-self.drawMargin),
                           self.cx+(self.r-self.drawMargin),
                           self.cy+(self.r-self.drawMargin),
                           fill="#808080") #grey

    #actual draw function

    def draw(self,canvas):
        if self.selected: #make selection oval
            self.drawSelectedOval(canvas)
        #then make general draw
        self.drawOuterOval(canvas)
        self.drawInnerOval(canvas)
        if self.showInfo: #If it wants to show info
            canvas.create_text(self.cx,self.cy,text = self.label)

    #legality
    
    def inNode(self,xPar,yPar): #check for hover or click on node
        return ((self.cx-self.r <= xPar <= self.cx+self.r) and
                (self.cy-self.r <= yPar <= self.cy+self.r))

    def inNondisplayGroup(self,att): #for list of nondisplayed attributes
        return att in self.nondisplayGroup

class edge(Struct):
    def __init__(self,fromNode,toNode,edgeType,edgeLabel,selected,weight=1):
        #adjacencies
        self.fromNode = fromNode
        self.toNode = toNode
        self.width = 2 #for initial draw
        self.edgeType = edgeType
        self.edgeLabel = edgeLabel
        self.uniqueEdgeLabel = edgeLabel #distinguishes what one can change
        #and what one can't change
        self.weight = weight
        self.color = "black"
        self.selected = selected
        #information not to display in dashboard
        self.nondisplayGroup = ["uniqueEdgeLabel",
                "selected","showInfo","nondisplayGroup","fromNode","toNode"]
        #helper for clicks
        self.clickOvalR = 10
        self.clickOvalMargin = 20 #for makign edge selector
        self.charDict = {} #for adding additional information
    
    #equality; controversial decision, not sure if this is good choice

    def __eq__(self,other):
        return ((self.fromNode == self.fromNode and self.toNode == self.toNode)
            or (self.fromNode == self.toNode and self.toNode == self.fromNode
                and self.edgeType == "undirected"))

    def __repr__(self):
        return str(type(self).__name__) + "(" + str(self.uniqueEdgeLabel) + ")"

    #legality

    def incidentWith(self,node): #checks if node is incident with edge
        return (self.fromNode == node or self.toNode == node)

    def inEdge(self,event): #checks if our click was in the edge oval
        (x0,y0) = (self.fromNode.cx,self.fromNode.cy)
        (x1,y1) = (self.toNode.cx,self.toNode.cy)
        (midX0, midY0) = ((x0+x1)/2,(y0+y1)/2) #for clickOval
        (circleMidX,circleMidY) = ((x0+midX0)/2,(y0+midY0)/2)
        (clickOvalCX,clickOvalCY) = (circleMidX-self.clickOvalMargin,
                                        circleMidY-self.clickOvalMargin)
        return (clickOvalCX-self.clickOvalR <= event.x 
                    <= clickOvalCX+self.clickOvalR and
                clickOvalCY-self.clickOvalR <= event.y 
                    <= clickOvalCY+self.clickOvalR)
    #drawing

    #drawing helpers

    def drawHighlightEdge(self,canvas): #for when an edge is selected
        (x0,y0) = (self.fromNode.cx,self.fromNode.cy)
        (x1,y1) = (self.toNode.cx,self.toNode.cy)
        drawMargin = 5
        widthMargin = self.width + drawMargin
        if (self.edgeType == "undirected"):
            canvas.create_line(x0,y0,x1,y1,width = widthMargin, fill = "yellow")
        else:
            (midX0, midY0) = ((x0+x1)/2,(y0+y1)/2)
            #ensure arrow in background is slightly larger than arrow in the
            #foreground
            arrowPar = 24
            arrowTuple = (arrowPar,
                    arrowPar,arrowPar) #specifies how I want my arrow to look
            canvas.create_line(x0,y0,midX0,midY0,width = widthMargin, 
                fill="yellow", arrow = tk.LAST,arrowshape = arrowTuple)
            canvas.create_line(midX0,midY0,x1,y1,width = widthMargin,
                fill="yellow")

    #actual drawing

    def draw(self,canvas):
        if (self.selected): #highlight it
            self.drawHighlightEdge(canvas)
        #specify centers to anchor edge
        (x0,y0) = (self.fromNode.cx,self.fromNode.cy)
        (x1,y1) = (self.toNode.cx,self.toNode.cy)
        (midX0, midY0) = ((x0+x1)/2,(y0+y1)/2) #used for click oval
        if (self.edgeType == "undirected"):
            canvas.create_line(x0,y0,x1,y1,width = self.width,fill=self.color)
        else:
            arrowPar = 15
            arrowTuple = (arrowPar,
                    arrowPar,arrowPar) #specifies how I want my arrow to look
            canvas.create_line(x0,y0,midX0,midY0,width = self.width,
                arrow = tk.LAST,arrowshape = arrowTuple,fill=self.color)
            canvas.create_line(midX0,midY0,x1,y1,width = self.width,
                fill=self.color)
        #make clickOval
        (circleMidX,circleMidY) = ((x0+midX0)/2,(y0+midY0)/2)
        #place slightly off from edge
        (clickOvalCX,clickOvalCY) = (circleMidX-self.clickOvalMargin,
                                        circleMidY-self.clickOvalMargin)
        canvas.create_oval(clickOvalCX-self.clickOvalR,
                            clickOvalCY-self.clickOvalR,
                            clickOvalCX + self.clickOvalR,
                            clickOvalCY+self.clickOvalR)
        
