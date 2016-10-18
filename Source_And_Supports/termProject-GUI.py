#termProject-GUI.py
#contains all of the visualization component objects for developing the
#interface

#imports
import eventBasedAnimation
from structClass import Struct #saved in (structClass.py)
import classScript #saved in (classScript.py)
import termProject_WikiScraper as ws #saved in (termProject_WikiScraper.py)
import Tkinter as tk
import string

#helper functions

def textSize(canvas, text, font): #taken from hw4 writeup
    # Note that tkFont.Font.measure(text) and tkFont.Font.metrics("linespace")
    # were both unreliable, producing wrong results in some cases.
    # This is a bit crufty, but generally works...
    temp = canvas.create_text(0, 0, text=text, anchor="nw", font=font)
    (x0, y0, x1, y1) = canvas.bbox(temp)
    canvas.delete(temp)
    return (x1-x0, y1-y0)

#THINGS TO FIX
#1. clean buttonInitiator

#classes

class reportTab(Struct): #put on the side for discussing metrics and information
    def __init__(self,x0,y0,width,height,graph,universalStorage,selectedItem):
        #location and color
        self.x0 = x0
        self.y0 = y0
        self.color = "light blue"
        self.width = width
        self.height = height
        self.margin = 5 #for drawing
        #information on the graph and stored information
        self.graph = graph
        self.universalStorage = universalStorage
        self.selectedItem = selectedItem
        #area to include metrics
        self.entryBoxList = []
        self.metricBoxList = []

    def resetInfo(self): #resetting all info
        self.selectedItem = None
        self.entryBoxList = []
        self.metricBoxList = []

    def storeObjInfo(self,obj): # for storing objects in info deck
        #location figures for information in info deck
        yBuff = 30
        bufferMargin = 5
        yHeight = 15
        boxX0 = self.x0 + self.margin
        boxWidth = self.width - 2*self.margin
        #add object
        self.selectedItem = obj
        self.entryBoxList = [] #restart to make new buttons
        self.metricBoxList = [] #restart to make new metric boxes
        for att in self.selectedItem.__dict__:
            #if charDict, we go into the chardict
            if (att not in self.selectedItem.nondisplayGroup 
                and att != "charDict"):
                (label,info) = (att,self.selectedItem.__dict__[att])
                #we leave x and y as none so that we can generate this location
                #as we draw the report tab
                #make entry button
                newEntryButton = entryBox(x0 = boxX0,y0 = yBuff,
                    width = boxWidth, height = yHeight, selected=False,
                    consideredObj = self.selectedItem,
                    label = label, info = info,typeReq = type(info), 
                    universalStorage = self.universalStorage,
                    reportTabWidth = self.width,
                    reportTabHeight = self.height,graph = self.graph)
                #keep track of height of entry buttons
                yBuff += yHeight + bufferMargin
                self.entryBoxList.append(newEntryButton)
            elif (att == "charDict"):
                yBuff += yHeight + bufferMargin #do this to make sure
                #we can fit Metric item in
                charDict = self.selectedItem.__dict__[att]
                for char in charDict: #make a metric box
                    (label, info) = (char,charDict[char])
                    newMetricBox = metricBox(x0 = boxX0,y0 = yBuff,
                                            width = boxWidth, height = yHeight,
                                            selected=False, 
                                            consideredObj = self.selectedItem, 
                                            label = label, info = info,
                                            typeReq = type(info), 
                                    universalStorage = self.universalStorage,
                                    reportTabWidth = self.width,
                                    reportTabHeight = self.height,
                                    graph = self.graph)
                    self.metricBoxList.append(newMetricBox)
                    #keep track of height on metric buttons
                    yBuff += yHeight + bufferMargin

    #mouse and key functions

    def onMouse(self,event): #this is a click
        for entryBox in self.entryBoxList:
            if (entryBox.onEntryBox(event)):
                givenEntryBox = entryBox
                givenEntryBox.selected = True
                for entryBox in self.entryBoxList:
                    if (entryBox != givenEntryBox): entryBox.selected = False
                return

    def onKey(self,event): #a key entrance event
        for entryBox in self.entryBoxList:
            if (entryBox.selected):
                entryBox.onKey(event)

    #legality

    def onReportTab(self,event): #check for instance on report tab
        return ((self.x0 <= event.x <= self.x0 + self.width) and 
                (self.y0 <= event.y <= self.y0 + self.height))

    def draw(self,canvas):
        font = "Arial 18 bold"
        prevText = "Report Tab"
        sucText = "Metrics"
        bufferMargin = 5
        #lay out rectangle of the report tab
        x1 = self.x0+self.width
        y1 = self.y0+self.height
        canvas.create_rectangle(self.x0+self.margin,self.y0+self.margin,
                        x1-self.margin,y1-self.margin,fill = self.color)
        #lay out report tab title and entry boxes
        canvas.create_text((self.x0+x1)/2,self.y0+self.margin,font = font,
            text = prevText,anchor = "n")
        for entryBox in self.entryBoxList: entryBox.draw(canvas)
        #then lay out metrics
        if (len(self.metricBoxList) > 0): #have metrics
            #find location for Metrics title
            lastEntryBox = self.entryBoxList[len(self.entryBoxList)-1]
            lastY1 = lastEntryBox.y0 + lastEntryBox.height
            canvas.create_text((self.x0+x1)/2,lastY1+bufferMargin,
                font=font, text = sucText, anchor = "n")
            #then draw our metric boxes
            for metricBox in self.metricBoxList: metricBox.draw(canvas)
        

class metricBox(Struct):
    def __init__(self,x0,y0,width,height,selected,consideredObj,
                 label,info,typeReq,universalStorage,reportTabWidth,
                 reportTabHeight,graph):
        #not cx and cy because entry boxes are anchored north
        self.x0 = x0
        self.y0 = y0
        self.width = width
        self.height = height
        self.selected = selected
        #object rrelated to metric box
        self.consideredObj = consideredObj
        self.label = label
        self.info = str(info)
        self.typeReq = typeReq #for requiring certain types of storage
        self.printableString = self.label + " : " + self.info
        self.editIndex = len(self.printableString)
        self.universalStorage = universalStorage
        #for information on bounds of entry
        self.reportTabWidth = reportTabWidth
        self.reportTabHeight = reportTabHeight
        #graph in reference to the metric box
        self.graph = graph

    def draw(self,canvas):
        textFont = "Arial 14 bold"
        boxFill = "" #interior fill is empty
        textFill = "black"
        (recX1,recY1) = (self.x0+self.width,self.y0+self.height)
        canvas.create_text((self.x0+recX1)/2,(self.y0+recY1)/2,
                text = self.printableString,font = textFont,
                fill = textFill)

class entryBox(metricBox):

    #init taken from metricBox

    #legality

    def onEntryBox(self,event): #need to know when we click on it
        return ((self.x0 <= event.x <= self.x0 + self.width) 
                and (self.y0 <= event.y <= self.y0 + self.height))
    
    def passesInfoLegalities(self,printableString): #helper for making sure
    #info placed in this is legal
        try:
            #makes sure this division occcurs once and only once
            assert(printableString.find(" : ") != -1) #require colon
            consideredInfoSet = printableString.split(" : ")
            consideredInfo = consideredInfoSet[1] #should occure after " : "
            try:
                testableInfo = eval(consideredInfo)
            except: #non-evaluatable form
                testableInfo = consideredInfo
            #check to see if it follows our type requirements
            assert(type(testableInfo) == self.typeReq 
                    or (self.label == "label")
                    or (self.label == "edgeLabel"))
            #bounds look up method: In the future, turn into dictionary
            #radii
            if (consideredInfoSet[0] == "r"
                or consideredInfoSet[0] == "clickOvalMargin"): #radius
                (minR, maxR) = (10,50)
                assert(minR <= testableInfo <= maxR) #control size
            #draw margins
            elif (consideredInfoSet[0] == "drawMargin"
                or consideredInfoSet[0] == "clickOvalR"):
                (minMarg,maxMarg) = (5,10)
                assert(minMarg <= testableInfo <= maxMarg)
            #centering
            elif (consideredInfoSet[0] == "cy"):
                (minCy, maxCy) = (0,self.reportTabHeight)
                assert(minCy <= testableInfo <= maxCy)
            elif (consideredInfoSet[0] == "cx"):
                (minCx, maxCx) = (0,self.x0)
                assert(minCx <= testableInfo <= maxCx)
            #weight
            elif (consideredInfoSet[0] == "weight"):
                assert(testableInfo > 0)
            #color
            elif (consideredInfoSet[0] == "color"):
                assert (testableInfo == "black"
                        or testableInfo == "green"
                        or testableInfo == "blue"
                        or testableInfo == "red")
            #type of edge
            elif (consideredInfoSet[0] == "edgeType"):
                assert(testableInfo == "directed"
                       or testableInfo == "undirected")
            #width
            elif (consideredInfoSet[0] == "width"):
                (minWidth,maxWidth) = (1,5)
                assert(minWidth <= testableInfo <= maxWidth)
            #passes our requirements, return true
            return True
        except: #didn't pass our rules, so return false
            return False

    #mouse and key functions

    def onKey(self,event):
        midIndex = self.printableString.find(":") #finding dif between
        #label and info
        maxInfoLength = 32 #controls info growth
        if (event.keysym == "Left"):
            if (self.editIndex > midIndex+2): #not at beginning of info
                self.editIndex -= 1
        elif (event.keysym == "Right"):
            if (self.editIndex < len(self.printableString)): #not at end of
            #info
                self.editIndex += 1
        elif (event.keysym == "BackSpace"): #delete info
            if (self.editIndex > midIndex+2):
                self.printableString = (self.printableString[:self.editIndex-1] +
                                        self.printableString[self.editIndex:])
                self.editIndex -= 1
        elif (event.keysym == "space" or event.keysym == "underscore"
            or event.keysym == "minus"): #add a space representation, i.e.
            #an underscore
            if (len(self.printableString) < maxInfoLength):#controls info growth
                #add underscrore to string
                self.printableString = (self.printableString[:self.editIndex]
                                + "_" + self.printableString[self.editIndex:])
                self.editIndex += 1
        #some factors to account for keysym output differences in
        #eventBasedAnimation: in
        #the future, a dict lookup may be more appropriate
        elif (event.keysym == "parenleft"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] 
                                + "(" + self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "parenright"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] 
                                + ")" + self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "slash"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] 
                                + "/" + self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "backslash"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] 
                                + "\\" + self.printableString[self.editIndex:])
                self.editIndex += 1
        elif ((str(event.keysym) in string.ascii_letters or 
               str(event.keysym) in string.digits) and
               len(str(event.keysym)) == 1): #ensures a single char entry
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] 
                   + str(event.keysym) + self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "bracketleft"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] 
                                + "[" + self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "bracketright"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] 
                                + "]" + self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "braceleft"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] 
                                + "{" + self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "braceright"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] 
                                + "}" + self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "Return"):
            #attempt to add new information, as long as it passed the legalities
            if (self.passesInfoLegalities(self.printableString)):
                #splits label and info
                infoSet = self.printableString.split(" : ")
                (label,newInfo) = (infoSet[0],infoSet[1])
                try:
                    self.consideredObj.__dict__[label] = eval(newInfo)
                except:
                    self.consideredObj.__dict__[label] = newInfo
                self.info = newInfo #update info
                #update printable string
                self.printableString = self.label + " : " + self.info
                self.selected = False #de-select value
            else: #did not pass legalities, try to edit again
                self.printableString = self.label + " : " + self.info
                self.editIndex = len(self.printableString)

    #drawing

    def draw(self,canvas):
        textFont = "Arial 14 bold"
        #choose box color and text color/fill
        if (self.selected):
            boxFill = "dark blue"
            textFill = "white" #to work with new background
        else:
            boxFill = "" #interior fill is empty
            textFill = "black"
        #then set box drawing
        (recX1,recY1) = (self.x0+self.width,self.y0+self.height)
        canvas.create_rectangle(self.x0,self.y0,recX1,recY1,fill = boxFill)
        #then check where to center the text in the box and what to do when
        #the string may be too long for the current box
        consideredString = self.printableString.split(" : ")
        minEditIndex = len(consideredString[0]) + len(" : ")
        editableText = consideredString[1]
        distFromEditIndex = 16
        #in the case of an edit box, get information on which text is
        #editable and what is the index of edit using this calculation
        translatedEditIndex = self.editIndex - minEditIndex
        addedEditIndexDecrease = (len(editableText[:translatedEditIndex]) 
                                - len(editableText[
                    translatedEditIndex-distFromEditIndex:translatedEditIndex]))
        if (translatedEditIndex > distFromEditIndex):
            editableText = (editableText[translatedEditIndex-distFromEditIndex:
                                        translatedEditIndex] + editableText[
                    translatedEditIndex:translatedEditIndex+distFromEditIndex])
        else:
            addedEditIndexDecrease = 0
            editableText = (editableText[:translatedEditIndex] + editableText[
                    translatedEditIndex:translatedEditIndex+distFromEditIndex])
        #now draw the string
        consideredString = consideredString[0] + " : " + editableText
        translatedEditIndex += (minEditIndex - addedEditIndexDecrease)
        if (self.selected): #need to set an edit box and a highlight on the
            #character to edit
            (printableStringWidth,printableStringHeight) = textSize(canvas,
                                                consideredString,textFont)
            if (consideredString[translatedEditIndex:] == ""): #end of string
                (grayBoxX0,grayBoxY0) = ((self.x0+recX1)/2 
                                        + printableStringWidth/2,self.y0)
                boxBuffer = 10 #for the gray box x1
                (grayBoxX1,grayBoxY1) = (grayBoxX0 + boxBuffer,
                                         self.y0+self.height)
                #then dray the highlight
                canvas.create_rectangle(grayBoxX0,grayBoxY0,grayBoxX1,grayBoxY1,
                                        fill = "gray", width = 0)
            else: #I need to draw edit box on a particular letter
                printableStringLeft = (self.x0+recX1)/2 - printableStringWidth/2
                #get width and height of substrings before and after this
                #particular letter
                (subStringWidth,subStringHeight) = textSize(canvas,
                                consideredString[:translatedEditIndex],textFont)
                (succeedStringWidth,succeedStringHeight) = textSize(canvas,
                              consideredString[translatedEditIndex+1:],textFont)
                #calculate left and right of this highlighted character using
                #widths of the string prior to it and the string succeeding it
                left =  printableStringLeft + subStringWidth
                right = (printableStringLeft +
                            printableStringWidth - succeedStringWidth)
                (top,bottom) = (self.y0,self.y0 + succeedStringHeight)
                #then draw highlight
                canvas.create_rectangle(left,top,right,bottom,
                    fill="gray",width = 0)
        #then simply generate the text
        canvas.create_text((self.x0+recX1)/2,(self.y0+recY1)/2,
                text = consideredString,font = textFont,
                fill = textFill)

class nodeMakerButton(Struct): #button used for generating nodes on the
    #page
    def __init__(self,x0,y0,width,height,text,selected,
                  graph,universalStorage,reportTab):
        #bounds
        self.x0 = x0
        self.y0 = y0
        self.width = width
        self.height = height
        #text information
        self.text = text
        self.selected = selected #meant to start program with nodeMaker Selected
        self.color = "light blue"
        #graph associated with the button
        self.graph = graph
        self.universalStorage = universalStorage #meant to be info dictionary
        self.reportTab = reportTab #to connect it with reporting information

    #legality

    def inButton(self,event):
        return ((self.x0 <= event.x <= self.x0+self.width) and
                (self.y0 <= event.y <= self.y0+self.width))

    #mouse and key functions

    def onMouse(self, event): #select a node after click in this context
        for node in self.graph.nodeSet:
            if node.inNode(event.x,event.y): #clicked on this
                selectedNode = node
                selectedNode.selected = True
                #unselect any previously selected nodes
                for node in self.graph.nodeSet:
                    if (node != selectedNode): node.selected = False
                #get information on selected node on the report tab
                self.reportTab.storeObjInfo(selectedNode)
                return #to prevent next section
        #if none of the clicks land on a node, generate a new one
        for node in self.graph.nodeSet:
            node.selected = False #reset
        newNode = classScript.node(cx=event.x,cy=event.y,
                                   r=self.universalStorage.r, 
                            label=self.universalStorage.nodeDefaultLabelCounter)
        #iterate the default label counter
        self.universalStorage.nodeDefaultLabelCounter += 1
        #add the node
        self.graph.nodeSet.add(newNode)
        #and store that information on the report tab
        self.reportTab.storeObjInfo(newNode)

    def onMouseDrag(self,event): #move around the tab
        for node in self.graph.nodeSet:
            #ensure that this move will occur on the selected node and
            #the drag will not occur when done on the report tab
            if (node.selected and not(self.reportTab.onReportTab(event))):
                (node.cx,node.cy) = (event.x,event.y)
                self.reportTab.storeObjInfo(node)

    def onMouseRelease(self,event):
        pass #not important currently

    def onKey(self,event): #set particular changes to selected nodes based
        #on arrow keys and deletion key
        if (event.keysym == "Up"): #increase node radius
            for node in self.graph.nodeSet:
                if (node.selected): 
                    maxR = 50 #upper bound on radius
                    if (node.r <= maxR):
                        node.r += 1
                        self.reportTab.storeObjInfo(node)
        elif (event.keysym == "Down"): #decrease node radius
            for node in self.graph.nodeSet:
                if (node.selected):
                    minR = 10 #lower bound on node radius
                    if (node.r >= minR):
                        node.r -= 1
                        self.reportTab.storeObjInfo(node)
        elif (event.keysym == "d"): #deletion key
            for node in self.graph.nodeSet:
                if (node.selected): 
                    self.graph.removeNode(node)
                    self.reportTab.resetInfo()
                    return

    #drawing

    def draw(self,canvas):
        #draw rectangle for button
        canvas.create_rectangle(self.x0,self.y0,self.x0+self.width,
                                self.y0 + self.height, fill = self.color)
        #place text in button
        canvas.create_text(self.x0+self.width/2, self.y0+self.height/2,
                           text = self.text,font= "Arial 14 bold")

class edgeMakerButton(nodeMakerButton): #used for dragging and generating
    #eges
    def __init__(self,x0,y0,width,height,text,selected,
                  graph,universalStorage,reportTab,drawingEdge,castingEdge):
        self.x0 = x0
        self.y0 = y0
        self.width = width
        self.height = height
        self.text = text
        self.selected = selected #start with nodeMaker Selected
        self.color = "light blue"
        self.graph = graph
        self.universalStorage = universalStorage
        self.reportTab = reportTab
        #helpers to indicate when I am drawing an edge (dragging the mouse)
        #and when I am casting said edge (when I simply initialize edge
        #creation with a mouse click
        self.drawingEdge = drawingEdge
        self.castingEdge = castingEdge
        self.edgeType = "undirected" #just initially

    #inherits legalities from nodeMakerButton

    #mouse and key functions

    #mouse and key helpers

    def inSetOfNodes(self,nodeI,nodeJ): #check if in nodes for a given edge
        #being casted
        return ((nodeI.inNode(self.edgeOrigX,self.edgeOrigY)) 
            and nodeJ.inNode(self.edgeEndX,self.edgeEndY))

    def resetProcesses(self): #clear drawing processes
        self.edgeOrigX = self.edgeOrigY = self.edgeEndX = self.edgeEndY = None
        self.castingEdge = self.drawingEdge = False

    #actual mouse and key functions

    def onMouse(self,event):
        for button in self.legalityButtonList:
            if (button.inButton(event)): #if on a certain button, perform that
                                        #button's mechanisms
                button.onMouse(event)
                return
        for edge in self.graph.edgeSet:
            if (edge.inEdge(event)): #select that edge and deselect others
                edge.selected = True
                #deselect other edges
                for othEdge in self.graph.edgeSet:
                    if (othEdge != edge): othEdge.selected = False
                self.reportTab.storeObjInfo(edge)
                return
        (self.edgeOrigX,self.edgeOrigY) = (event.x,event.y) #save for drag
        self.castingEdge = True #helps fix bugs with drag rules

    def onMouseDrag(self,event):
        if (self.castingEdge): #if we have a self.edgeOrigX and self.edgeOrigY
            (self.edgeEndX,self.edgeEndY) = (event.x,event.y)
            self.drawingEdge = True #representative of drag occuring

    def onMouseRelease(self,event):
        if (self.drawingEdge): #check to see if edge being drawn lands between
                                #two nodes
            for nodeI in self.graph.nodeSet:
                tempNodeList = list(self.graph.nodeSet)
                tempNodeList.remove(nodeI)
                for nodeJ in tempNodeList:
                    if (self.inSetOfNodes(nodeI,nodeJ)): #in this node set
                        #make edge and add it manually
                        newEdge = classScript.edge(fromNode = nodeI,
                            toNode = nodeJ,edgeType = self.edgeType,
                            selected = True,edgeLabel = 
                            self.universalStorage.edgeDefaultLabelCounter,
                            weight=1)
                        self.graph.add_edge_man(newEdge,nodeI,nodeJ)
                        self.universalStorage.edgeDefaultLabelCounter += 1
                        self.resetProcesses() #resets casting parameters
                        for edge in self.graph.edgeSet: #deselections
                            if edge != newEdge: edge.selected = False
                        self.reportTab.storeObjInfo(newEdge)
                        return #stops looking at nodes
            #couldn't find any node incidence being drawn, reset processes
            self.resetProcesses()

    def onKey(self,event):
        if (event.keysym == "d"): #edge deletion
            for edge in self.graph.edgeSet:
                if edge.selected:
                    self.graph.removeEdge(edge)
                    self.reportTab.resetInfo()
                    break

    #draw helpers

    def edgeCaster(self,canvas): #visual for when casting edge
        if (self.edgeType == "undirected"):
            canvas.create_line(self.edgeOrigX, self.edgeOrigY, self.edgeEndX,
                            self.edgeEndY,width=2)
        else: #need an arrow
            #draw triangle
            (midX0, midY0) =  ((self.edgeOrigX+self.edgeEndX)/2,
                                (self.edgeOrigY + self.edgeEndY)/2)
            arrowPar = 15
            arrowTup = (arrowPar,arrowPar,arrowPar)
            canvas.create_line(self.edgeOrigX, self.edgeOrigY, midX0,
                            midY0,width=2, arrow = tk.LAST,
                            arrowshape = arrowTup)
            canvas.create_line(midX0, midY0, self.edgeEndX,
                            self.edgeEndY,width=2)

class wikiScraperButton(nodeMakerButton): #button to initiate scraping of
    #wikipedia
    #inherits most capacities from nodeMakerButton
    def __init__(self,x0,y0,selected,width,height,text,graph,reportTab):
        self.x0 = x0
        self.y0 = y0
        self.selected = selected
        self.color = "light blue"
        self.width = width
        self.height = height
        self.text = text
        self.graph = graph
        self.reportTab = reportTab

    #mouse functions

    def onMouse(self, event):
        pass

    def onMouseDrag(self,event):
        pass

    def onMouseRelease(self,event):
        pass #not important currently

    def onKey(self,event):
        pass

class metricBuilderButton(wikiScraperButton): 
    #init; stays the same
    def onMouse(self,event):
        #run metric builder
        if (len(self.graph.nodeSet) > 0): #cannot do a case with a null graph
            self.graph.buildMetrics()
            #load in metric information for selected objects
            for node in self.graph.nodeSet:
                if (node.selected):
                    self.reportTab.storeObjInfo(node)
                    return
            for edge in self.graph.edgeSet:
                if (edge.selected):
                    self.reportTab.storeObjInfo(edge)
                    return

class edgeLegalityButton(edgeMakerButton):

    #initialization

    def __init__(self,x0,y0,width,height,selected,text,
                    assocEdgeMakerButton,edgeType):
        self.x0  = x0
        self.y0 = y0
        self.width = width
        self.height = height
        self.color = "light blue"
        self.selected = selected
        self.text = text
        self.assocEdgeMakerButton = assocEdgeMakerButton
        self.edgeType = edgeType

    #mouse and key functions

    def onMouse(self,event):
        if (self.assocEdgeMakerButton.selected): #only shows when we are
            #making edges
            #make edge maker button use this new edge type
            self.assocEdgeMakerButton.edgeType = self.edgeType

    def onMouseDrag(self,event):
        pass

    def onMouseRelease(self,event):
        pass

    def onKey(self,event):
        pass

    #draw function

    def draw(self,canvas):
        if self.assocEdgeMakerButton.selected: #only shows when we are making
            #edges
            canvas.create_rectangle(self.x0,self.y0,self.x0+self.width,
                                self.y0 + self.height, fill= self.color)
            canvas.create_text(self.x0+self.width/2, self.y0+self.height/2,
                           text = self.text,font= "Arial 14 bold")

class bfsButton(metricBuilderButton): #for running aspects of bfs from a given
    #node
    #init; stays the same
    def onMouse(self,event):
        for node in self.graph.nodeSet:
            if (node.inNode(event.x,event.y)): #perform BFS starting at that
                #node
                self.graph.performBFS(node)
                node.selected = True
                self.reportTab.storeObjInfo(node)
                for othNode in self.graph.nodeSet:
                    if (othNode != node): othNode.selected = False
                for edge in self.graph.edgeSet: edge.selected = False
                return True #performed BFS
        return False #did not perform BFS

class nodeGUI(eventBasedAnimation.Animation):

	#initialization

	#helpers for initialization

    def initiateMakerButtons(self):
        self.nodeMakerButton = nodeMakerButton(x0=self.buttonMargin,
                                y0=self.height-self.buttonHeight,
                                width = self.buttonWidth,
                                 height = self.buttonHeight,text="Node Creator",
                                selected = True, graph = self.graph,
                                universalStorage = self.universalStorage,
                                reportTab=self.reportTab)
        self.edgeMakerButton = edgeMakerButton(x0=(self.buttonWidth
                    +self.buttonMargin*2),y0=self.height-self.buttonHeight,
                    width = self.buttonWidth,height=self.buttonHeight,
                    text = "Edge Creator",selected = False, graph = self.graph,
                    universalStorage=self.universalStorage,
                    reportTab=self.reportTab,
                    castingEdge=False,drawingEdge=False)

    def initiateEdgeLegalityButtons(self):
        #one for undirected edge creation
        self.undirEdgeButton = edgeLegalityButton(x0 = self.edgeMakerButton.x0, 
            y0= self.edgeMakerButton.y0-self.buttonHeight,selected = False,
            width = self.buttonWidth/2,height = self.buttonHeight, text="Undir",
            assocEdgeMakerButton = self.edgeMakerButton,edgeType = "undirected")
        #one for directed edge creation
        self.dirEdgeButton = edgeLegalityButton(
            x0 = self.undirEdgeButton.x0 + self.buttonWidth/2, 
            y0 = self.undirEdgeButton.y0, selected = False,
            width = self.buttonWidth/2, height = self.buttonHeight,
            text = "Dir", assocEdgeMakerButton = self.edgeMakerButton,
            edgeType="directed")

    def initiateWikiScraperButton(self):
        self.wikiScraperButton = wikiScraperButton(x0 = self.edgeMakerButton.x0+
            self.buttonWidth + self.buttonMargin,y0 = self.edgeMakerButton.y0,
            selected = False, width = self.buttonWidth,
            height = self.buttonHeight, text = "WikiScraper",graph=self.graph,
            reportTab = self.reportTab)

    def initiateMetricBuilderButton(self):
        self.metricBuilderButton = metricBuilderButton(
            x0 = self.wikiScraperButton.x0 + self.buttonWidth 
                        + self.buttonMargin,
            y0 = self.edgeMakerButton.y0,selected = False,
            width = self.buttonWidth,height = self.buttonHeight,
            text = "Metric Builder",graph=self.graph,reportTab = self.reportTab)

    def initiateBFSButton(self):
        self.bfsButton = bfsButton(
            x0 = self.metricBuilderButton.x0 +
                self.buttonWidth + self.buttonMargin,
            y0 = self.edgeMakerButton.y0,selected = False,
            width = self.buttonWidth,height = self.buttonHeight,text = "BFS",
            graph=self.graph,reportTab = self.reportTab)

    def buttonInitiator(self): #helper to make buttons
        #store some button size constants
        self.buttonWidth = 100
        self.buttonHeight =  30
        self.buttonMargin = 10 #for margin
        #then initiate our buttons
        self.initiateMakerButtons() #gets edge and nodemaker
        self.initiateEdgeLegalityButtons() #gets my legality buttons
        self.initiateWikiScraperButton()
        self.initiateMetricBuilderButton()
        self.initiateBFSButton()
        self.edgeMakerButton.legalityButtonList = [self.undirEdgeButton,
        self.dirEdgeButton] #needed to add this after generating the
        #edge maker button and buttons for altering edge type drawn
        self.buttonList = [self.nodeMakerButton,self.edgeMakerButton,
                self.wikiScraperButton,self.metricBuilderButton,self.bfsButton,
                self.undirEdgeButton,self.dirEdgeButton]
	
    def reportInitiator(self): #makes report tab
        tabDiv = 3 #should take up a third of the GUI
        (tabWidth,tabHeight) = (self.width / tabDiv,self.height)
        (x0,y0) = (self.width-tabWidth,0)
    	self.reportTab = reportTab(x0 = x0,y0 = y0,
            width = tabWidth, height = tabHeight,graph = self.graph,
            universalStorage = self.universalStorage,selectedItem=None)

	#actual initialization

    def onInit(self):
        self.graph = classScript.graph()
        #so other objects can reference to this struct
        self.universalStorage = Struct(r = 30,nodeDefaultLabelCounter = 0,
                                       edgeDefaultLabelCounter = 0)
        #initialize report tab and buttons
        self.reportInitiator()
        self.buttonInitiator() #helps make buttons
        self.entryActive = False
        self.link = "" #handle this later for entry
        self.entryCounter = 0
        self.bfsActive = False

    #mouse and key functions

    #helpers for mouse and key functions

    def entryReset(self): #meant for resetting particular information request
        #events (specifically requesting information for the wikiscraper)
        self.entryActive = False
        self.link = ""
        (self.entryCounter,self.maxEntryCounter) = (0,0)
        (self.entryList,self.entryListReq) = ([],[])

    def requirementChecker(self): #helper that checks if a given request
        #(mainly during an entryActive situation)
        try:
            self.link = eval(self.link)
            if type(self.link) == self.entryListReq[self.entryCounter]:
                #append information written during this phase
                self.entryList.append(self.link)
                self.link = "" #reset
                self.entryCounter += 1
            else:
                self.link = "" #try again
        except: #we have a string
            #correct one
            if type(self.link) == self.entryListReq[self.entryCounter]:
                self.entryList.append(self.link)
                self.link = "" #reset
                self.entryCounter += 1
            else: #didn't work by requirements
                self.link = "" #try again

    def parseForWikiGraph(self, entryList): #help to parse list for tuple
        link = entryList[0]
        if ("/wiki/" not in link): #an important handle
            link = "/wiki/" + link #we made sure it was a string, so this has
            #to be legal.
        depth = entryList[1]
        maxDepth = 8 #I set this so that our graph doesn't grow arbitrarily
        #huge
        if (depth > maxDepth): depth = maxDepth
        maxDegree = 100 #I set this so that our graph doesn't grow arbitrarily
        #huge
        degreeInd = 2
        degree = entryList[degreeInd]
        if (degree > maxDegree): degree = maxDegree
        return (link,depth,degree)

    def entryActiveKey(self,event): #key rules during entryActive phase
        if (event.keysym == "Return"):
            self.requirementChecker() #checks if it satisfies our requirements
            if self.entryCounter == self.maxEntryCounter: #got all entries,
                #let us scrpe for the wikipedia graph
                (link,depth,degree) = self.parseForWikiGraph(self.entryList)
                self.graph = ws.buildWikiGraph(link,depth,degree,
                    self.reportTab.x0,self.nodeMakerButton.y0)
                self.graph.wikiCleaner() #cleans graph after a wiki scrape
                #then update graph across the board to this wiki-scraped
                #graph
                self.reportTab.graph = self.edgeMakerButton.graph = self.nodeMakerButton.graph = self.graph
                self.wikiScraperButton.graph = self.metricBuilderButton.graph = self.bfsButton.graph = self.graph
                self.entryReset()
                self.reportTab.resetInfo()
        #typical entry rules for keystrokes
        elif (event.keysym == "BackSpace"): #remove the last character
            self.link = self.link[:len(self.link)-1]
        elif (event.keysym == "parenleft"):
            self.link += "("
        elif (event.keysym == "parenright"):
            self.link += ")"
        elif (event.keysym == "underscore" or event.keysym == "space"):
            self.link += "_"
        elif (event.keysym == "slash"): self.link += "/"
        elif (event.keysym == "backslash"): self.link += "\\"
        elif ((str(event.keysym) in string.ascii_letters or 
            str(event.keysym) in string.digits) and
            len(str(event.keysym)) == 1):
            self.link += str(event.keysym)

    #legality functions

    def inAnimationBounds(self,event):
        return (0 <= event.x <= self.width and 0 <= event.y <= self.height)

    #actual mouse and key functions

    def onMouse(self, event):
        if (self.bfsActive): #choose a bfs
            performedBFS = self.bfsButton.onMouse(event) #sends back truth
            #value if performed breadth-first search
            if (performedBFS):
                self.bfsActive = False
        else: #see where we clicked
            if (not(self.entryActive)):
                if (self.reportTab.onReportTab(event)):
                    self.reportTab.onMouse(event)
                    return
                for button in self.buttonList:
                    if (button.inButton(event) 
                        and type(button) == metricBuilderButton):
                        button.onMouse(event)
                        return
                    elif (button.inButton(event) 
                        and type(button) == bfsButton):
                        self.bfsActive = True
                        return
                    elif (button.inButton(event) 
                        and type(button) == wikiScraperButton): #move into
                        #entry mode
                        self.entryActive = True
                        self.entryText = [
                                "Please write your starting page handle.",
                                "Please write the max depth (as an integer).",
                                "Please write the max degree (as an integer)."]
                        self.maxEntryCounter = len(self.entryText)
                        self.entryCounter = 0
                        self.entryList = []
                        self.entryListReq = [str, int, int] #requirements on 
                        #entry
                        return
                    elif (button.inButton(event) and 
                        type(button) != edgeLegalityButton): #handle selection
                        #changes
                        givenButton = button
                        givenButton.selected = True
                        for button in self.buttonList:
                            if (button != givenButton): button.selected = False
                        for node in self.graph.nodeSet: #deselect all nodes
                            node.selected = False
                        for edge in self.graph.edgeSet: #deselect all edges
                            edge.selected = False
                        return #prevents going to commands
                #if we do not have one of our special cases above, just
                #perform the onMouse method on the part of the button
                for button in self.buttonList:
                    if (button.selected):
                        button.onMouse(event)

    def onMouseDrag(self,event):
        #check to see if certain special events are activated: if those
        #events are not activated, just go the drag functionality of the
        #selected button
        if (not(self.bfsActive)):
            if (not(self.entryActive)):
                if (self.inAnimationBounds(event)):
                    for button in self.buttonList:
                        if (button.selected): button.onMouseDrag(event)

    def onMouseRelease(self,event):
        #similar structure to onMouseDrag, but for onMouseRelease situations
        if (not(self.bfsActive)):
            if (not(self.entryActive)):
                if (self.inAnimationBounds(event)):
                    for button in self.buttonList:
                        if (button.selected): button.onMouseRelease(event)

    def onKey(self,event): #moves key clicks to particular objects of our
        #application
        if (not(self.bfsActive)):
            if self.entryActive:
                self.entryActiveKey(event)
                return
            else:
                reportTabEntryList = self.reportTab.entryBoxList
                for entryBox in reportTabEntryList:
                    if entryBox.selected:
                        entryBox.onKey(event)
                        return
                for button in self.buttonList:
                    if (button.selected): button.onKey(event)

    def onMouseMove(self,event): #for hover-overs on nodes
        if (self.inAnimationBounds(event)):
            for node in self.graph.nodeSet:
                if node.inNode(event.x,event.y):
                    node.showInfo = True
                else: node.showInfo = False

    #drawing functions

    #drawing helpers

    def drawEntryActiveScreen(self,canvas): #used for inputting information for
        #the wikiscraper
        r = 200
        (x0,y0,x1,y1) = (self.width/2-r,self.height/2-r, self.width/2+r,
                        self.height/2+r)
        #make rectange for the entry box
        canvas.create_rectangle(x0,y0,x1,y1,fill="gray")
        #description of information requested
        canvas.create_text(self.width/2,y0,
            text=self.entryText[self.entryCounter],font = "Arial 14 bold",
            anchor="n")
        #response being generated
        canvas.create_text(self.width/2,y0+r,text=str(self.link),
            font = "Arial 14 bold",anchor="n")

    #actual drawing functions

    def onDraw(self, canvas):
        self.graph.draw(canvas)
        if self.entryActive: #request information
            self.drawEntryActiveScreen(canvas)
        #for visualizing edge creation mid-draw
        if (self.edgeMakerButton.selected and self.edgeMakerButton.drawingEdge):
            self.edgeMakerButton.edgeCaster(canvas) #visual of casting edge
        for button in self.buttonList:
            button.draw(canvas)
        self.reportTab.draw(canvas)
        if (self.bfsActive):
            bfsTextMargin = 5
            canvas.create_text(bfsTextMargin,bfsTextMargin,
                text = "Click on a Node To Source Breadth First Search!",
                font = "Arial 14 bold", anchor = "nw")

#running the program

nodeGUI(width=1000, height=600,windowTitle = "Networks GUI",
    aboutText = "Networks GUI\nBy Michael Rosenberg",
    ).run()
