#termProject.py

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

class reportTab(Struct):
    def __init__(self,x0,y0,width,height,graph,universalStorage,selectedItem):
        self.x0 = x0
        self.y0 = y0
        self.color = "light blue"
        self.width = width
        self.height = height
        self.margin = 5 #for drawing
        self.graph = graph
        self.universalStorage = universalStorage
        self.selectedItem = selectedItem
        self.entryBoxList = []
        self.metricBoxList = []

    def resetInfo(self): #resetting all info
        self.selectedItem = None
        self.entryBoxList = []
        self.metricBoxList = []

    def storeObjInfo(self,obj): # for storing objects in info deck
        yBuff = 30
        bufferMargin = 5
        yHeight = 15
        boxX0 = self.x0 + self.margin
        boxWidth = self.width - 2*self.margin
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
                newEntryButton = entryBox(x0 = boxX0,y0 = yBuff,
                    width = boxWidth, height = yHeight, selected=False, consideredObj = self.selectedItem,
                    label = label, info = info,typeReq = type(info), 
                    universalStorage = self.universalStorage,reportTabWidth = self.width,
                    reportTabHeight = self.height,graph = self.graph)
                yBuff += yHeight + bufferMargin
                self.entryBoxList.append(newEntryButton)
            elif (att == "charDict"):
                yBuff += yHeight + bufferMargin #do this to make sure
                #we can fit Metric item in
                charDict = self.selectedItem.__dict__[att]
                for char in charDict:
                    (label, info) = (char,charDict[char])
                    newMetricBox = metricBox(x0 = boxX0,y0 = yBuff,
                        width = boxWidth, height = yHeight,
                        selected=False, consideredObj = self.selectedItem, label = label, info = info,
                        typeReq = type(info), 
                        universalStorage = self.universalStorage,reportTabWidth = self.width,
                        reportTabHeight = self.height,graph = self.graph)
                    self.metricBoxList.append(newMetricBox)
                    yBuff += yHeight + bufferMargin

    #mouse and key functions

    def onMouse(self,event):
        for entryBox in self.entryBoxList:
            if (entryBox.onEntryBox(event)):
                givenEntryBox = entryBox
                givenEntryBox.selected = True
                for entryBox in self.entryBoxList:
                    if (entryBox != givenEntryBox): entryBox.selected = False
                return

    def onKey(self,event):
        for entryBox in self.entryBoxList:
            if (entryBox.selected):
                entryBox.onKey(event)

    #legality

    def onReportTab(self,event):
        return ((self.x0 <= event.x <= self.x0 + self.width) and 
                (self.y0 <= event.y <= self.y0 + self.height))

    def draw(self,canvas):
        font = "Arial 18 bold"
        prevText = "Report Tab"
        sucText = "Metrics"
        bufferMargin = 5
        x1 = self.x0+self.width
        y1 = self.y0+self.height
        canvas.create_rectangle(self.x0+self.margin,self.y0+self.margin,
                        x1-self.margin,y1-self.margin,fill = self.color)
        canvas.create_text((self.x0+x1)/2,self.y0+self.margin,font = font,
            text = prevText,anchor = "n")
        for entryBox in self.entryBoxList: entryBox.draw(canvas)
        if (len(self.metricBoxList) > 0): #have metrics
            lastEntryBox = self.entryBoxList[len(self.entryBoxList)-1]
            lastY1 = lastEntryBox.y0 + lastEntryBox.height
            canvas.create_text((self.x0+x1)/2,lastY1+bufferMargin,
                font=font, text = sucText, anchor = "n")
            for metricBox in self.metricBoxList: metricBox.draw(canvas)
        

class metricBox(Struct):
    def __init__(self,x0,y0,width,height,selected,consideredObj,
        label,info,typeReq, universalStorage,reportTabWidth,reportTabHeight,
        graph):
        #not cx and cy because entry boxes are anchored north
        self.x0 = x0
        self.y0 = y0
        self.width = width
        self.height = height
        self.selected = selected
        self.consideredObj = consideredObj
        self.label = label
        self.info = str(info)
        self.typeReq = typeReq #for requiring certain types of storage
        self.printableString = self.label + " : " + self.info
        self.editIndex = len(self.printableString)
        self.universalStorage = universalStorage
        self.reportTabWidth = reportTabWidth
        self.reportTabHeight = reportTabHeight
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

    def onEntryBox(self,event):
        return (self.x0 <= event.x <= self.x0 + self.width) and (self.y0 
            <= event.y <= self.y0 + self.height)
    
    def passesInfoLegalities(self,printableString): #helper for making sure
    #info is good
        try:
            #makes sure this division occcurs once and only once
            assert(printableString.find(" : ") != -1)
            consideredInfoSet = printableString.split(" : ")
            consideredInfo = consideredInfoSet[1] #should occure after " : "
            try:
                testableInfo = eval(consideredInfo)
            except: #non-evaluatable form
                testableInfo = consideredInfo
            #check to see if it follows our type requirements
            assert(type(testableInfo) == self.typeReq or 
                (self.label == "label") or (self.label == "edgeLabel"))
            if (consideredInfoSet[0] == "r"
                or consideredInfoSet[0] == "clickOvalMargin"): #radius
                (minR, maxR) = (10,50)
                assert(minR <= testableInfo <= maxR) #control size
            elif (consideredInfoSet[0] == "drawMargin"
                or consideredInfoSet[0] == "clickOvalR"):
                (minMarg,maxMarg) = (5,10)
                assert(minMarg <= testableInfo <= maxMarg)
            elif (consideredInfoSet[0] == "cy"):
                (minCy, maxCy) = (0,self.reportTabHeight)
                assert(minCy<= testableInfo<=maxCy)
            elif (consideredInfoSet[0] == "cx"):
                (minCx, maxCx) = (0,self.x0)
                assert(minCx <= testableInfo <= maxCx)
            elif (consideredInfoSet[0] == "weight"):
                assert(testableInfo > 0)
            elif (consideredInfoSet[0] == "color"):
                assert (testableInfo == "black"
                    or testableInfo == "green"
                    or testableInfo == "blue"
                    or testableInfo == "red")
            elif (consideredInfoSet[0] == "edgeType"):
                assert(testableInfo == "directed"
                    or testableInfo == "undirected")
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
        elif (event.keysym == "BackSpace"):
            if (self.editIndex > midIndex+2):
                self.printableString = (self.printableString[:self.editIndex-1] +
                                        self.printableString[self.editIndex:])
                self.editIndex -= 1
        elif (event.keysym == "space" or event.keysym == "underscore"
            or event.keysym == "minus"):
            if (len(self.printableString) < maxInfoLength):#controls info growth
                self.printableString = (self.printableString[:self.editIndex] + "_" +
                                        self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "parenleft"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] + "(" +
                                        self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "parenright"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] + ")" +
                                        self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "slash"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] + "/" +
                                        self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "backslash"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] + "\\" +
                                        self.printableString[self.editIndex:])
                self.editIndex += 1
        elif ((str(event.keysym) in string.ascii_letters or 
            str(event.keysym) in string.digits) and
            len(str(event.keysym)) == 1):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] + str(event.keysym) +
                                        self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "bracketleft"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] + "[" +
                                        self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "bracketright"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] + "]" +
                                        self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "braceleft"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] + "{" +
                                        self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "braceright"):
            if (len(self.printableString) < maxInfoLength):
                self.printableString = (self.printableString[:self.editIndex] 
                    + "}" + self.printableString[self.editIndex:])
                self.editIndex += 1
        elif (event.keysym == "Return"):
            #create new info
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
            else:
                self.printableString = self.label + " : " + self.info
                self.editIndex = len(self.printableString)

    #drawing

    def draw(self,canvas):
        textFont = "Arial 14 bold"
        if (self.selected):
            boxFill = "dark blue"
            textFill = "white" #to work with new background
        else:
            boxFill = "" #interior fill is empty
            textFill = "black"
        (recX1,recY1) = (self.x0+self.width,self.y0+self.height)
        canvas.create_rectangle(self.x0,self.y0,recX1,recY1,fill = boxFill)
        consideredString = self.printableString.split(" : ")
        minEditIndex = len(consideredString[0]) + len(" : ")
        editableText = consideredString[1]
        distFromEditIndex = 16
        translatedEditIndex = self.editIndex-minEditIndex
        addedEditIndexDecrease = (len(editableText[:translatedEditIndex]) 
        - len(editableText[
            translatedEditIndex-distFromEditIndex:translatedEditIndex]))
        if (translatedEditIndex > distFromEditIndex):
            addedEditIndexDecrease = (len(editableText[:translatedEditIndex]) 
        - len(editableText[
            translatedEditIndex-distFromEditIndex:translatedEditIndex]))
            editableText = (editableText[translatedEditIndex-distFromEditIndex:
                                        translatedEditIndex] + editableText[
                    translatedEditIndex:translatedEditIndex+distFromEditIndex])
        else:
            addedEditIndexDecrease = 0
            editableText = (editableText[:translatedEditIndex] + editableText[
                    translatedEditIndex:translatedEditIndex+distFromEditIndex])
        consideredString = consideredString[0] + " : " + editableText
        translatedEditIndex += (minEditIndex - addedEditIndexDecrease)
        if (self.selected):
            (printableStringWidth,printableStringHeight) = textSize(canvas,
                consideredString,textFont)
            if (consideredString[translatedEditIndex:] == ""): #end of string
                (grayBoxX0,grayBoxY0) = ((self.x0+recX1)/2 
                    + printableStringWidth/2,self.y0)
                boxBuffer = 10 #for the gray box x1
                (grayBoxX1,grayBoxY1) = (grayBoxX0 + boxBuffer,
                                         self.y0+self.height)
                canvas.create_rectangle(grayBoxX0,grayBoxY0,grayBoxX1,grayBoxY1,
                    fill = "gray", width = 0)
            else:
                printableStringLeft = (self.x0+recX1)/2 - printableStringWidth/2
                (subStringWidth,subStringHeight) = textSize(canvas,
                    consideredString[:translatedEditIndex],textFont)
                (succeedStringWidth,succeedStringHeight) = textSize(canvas,
                    consideredString[translatedEditIndex+1:],textFont)
                left =  printableStringLeft+subStringWidth
                right = (printableStringLeft+
                    printableStringWidth-succeedStringWidth)
                (top,bottom) = (self.y0,self.y0 + succeedStringHeight)
                canvas.create_rectangle(left,top,right,bottom,
                    fill="gray",width = 0)
        canvas.create_text((self.x0+recX1)/2,(self.y0+recY1)/2,
                text = consideredString,font = textFont,
                fill = textFill)

class nodeMakerButton(Struct):
    def __init__(self,x0,y0,width,height,text,selected,
                  graph,universalStorage,reportTab):
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

    #legality

    def inButton(self,event):
        return ((self.x0 <= event.x <= self.x0+self.width) and
                (self.y0 <= event.y <= self.y0+self.width))

    #mouse and key functions

    #helpers for mouse and key functions

    #fix this up!

    #actual mouse and key functions

    def onMouse(self, event):
        for node in self.graph.nodeSet:
            if node.inNode(event.x,event.y): #clicked on this
                selectedNode = node
                selectedNode.selected = True
                for node in self.graph.nodeSet:
                    if (node != selectedNode): node.selected = False
                self.reportTab.storeObjInfo(selectedNode)
                return #to prevent next section
        for node in self.graph.nodeSet:
            node.selected = False #reset
        newNode = classScript.node(cx=event.x,cy=event.y,
                r=self.universalStorage.r, 
                label=self.universalStorage.nodeDefaultLabelCounter)
        self.universalStorage.nodeDefaultLabelCounter += 1
        self.graph.nodeSet.add(newNode)
        self.reportTab.storeObjInfo(newNode)

    def onMouseDrag(self,event):
        for node in self.graph.nodeSet:
            if (node.selected and not(self.reportTab.onReportTab(event))):
                (node.cx,node.cy) = (event.x,event.y)
                self.reportTab.storeObjInfo(node)

    def onMouseRelease(self,event):
        pass #not important currently

    def onKey(self,event):
        if (event.keysym == "Up"):
            for node in self.graph.nodeSet:
                if (node.selected): 
                    maxR = 50
                    if (node.r <= maxR):
                        node.r += 1
                        self.reportTab.storeObjInfo(node)
        elif (event.keysym == "Down"):
            for node in self.graph.nodeSet:
                if (node.selected):
                    minR = 10 
                    if (node.r >= minR):
                        node.r -= 1
                        self.reportTab.storeObjInfo(node)
        elif (event.keysym == "d"):
            for node in self.graph.nodeSet:
                if (node.selected): 
                    self.graph.removeNode(node)
                    self.reportTab.resetInfo()
                    return

    #drawing

    def draw(self,canvas):
        canvas.create_rectangle(self.x0,self.y0,self.x0+self.width,
                                self.y0 + self.height, fill= self.color)
        canvas.create_text(self.x0+self.width/2, self.y0+self.height/2,
                           text = self.text,font= "Arial 14 bold")

class edgeMakerButton(nodeMakerButton):
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
        self.drawingEdge = drawingEdge
        self.castingEdge = castingEdge
        self.edgeType = "undirected" #just initially

    #inherits legalities

    #mouse and key functions

    #mouse and key helpers

    def inSetOfNodes(self,nodeI,nodeJ): #check if in nodes
        return ((nodeI.inNode(self.edgeOrigX,self.edgeOrigY)) 
            and nodeJ.inNode(self.edgeEndX,self.edgeEndY))

    def resetProcesses(self):
        self.edgeOrigX = self.edgeOrigY = self.edgeEndX = self.edgeEndY = None
        self.castingEdge = self.drawingEdge = False

    #actual mouse and key functions

    def onMouse(self,event):
        for button in self.legalityButtonList:
            if (button.inButton(event)):
                button.onMouse(event)
                return
        for edge in self.graph.edgeSet:
            if (edge.inEdge(event)):
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
            self.drawingEdge = True

    def onMouseRelease(self,event):
        if (self.drawingEdge):
            for nodeI in self.graph.nodeSet:
                tempNodeList = list(self.graph.nodeSet)
                tempNodeList.remove(nodeI)
                for nodeJ in tempNodeList:
                    if (self.inSetOfNodes(nodeI,nodeJ)): #in this node set
                        newEdge = classScript.edge(fromNode = nodeI,
                            toNode = nodeJ,edgeType = self.edgeType,
                            selected = True,
                            edgeLabel = (
                                self.universalStorage.edgeDefaultLabelCounter),
                            weight=1)
                        self.graph.add_edge_man(newEdge,nodeI,nodeJ)
                        self.universalStorage.edgeDefaultLabelCounter += 1
                        self.resetProcesses() #resets casting parameters
                        for edge in self.graph.edgeSet: #deselections
                            if edge != newEdge: edge.selected = False
                        self.reportTab.storeObjInfo(newEdge)
                        return #stops looking at nodes
            #couldn't find anything, reset processes
            self.resetProcesses()

    def onKey(self,event):
        if (event.keysym == "d"):
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
            canvas.create_line(self.edgeOrigX, self.edgeOrigY, midX0,
                            midY0,width=2, arrow = tk.LAST,
                            arrowshape = (15,15,15))
            canvas.create_line(midX0, midY0, self.edgeEndX,
                            self.edgeEndY,width=2)

class wikiScraperButton(nodeMakerButton):
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
        self.graph.buildMetrics()
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
        if (self.assocEdgeMakerButton.selected):
            #inherit new edge type
            self.assocEdgeMakerButton.edgeType = self.edgeType

    def onMouseDrag(self,event):
        pass

    def onMouseRelease(self,event):
        pass

    def onKey(self,event):
        pass

    #draw function

    def draw(self,canvas):
        if self.assocEdgeMakerButton.selected:
            canvas.create_rectangle(self.x0,self.y0,self.x0+self.width,
                                self.y0 + self.height, fill= self.color)
            canvas.create_text(self.x0+self.width/2, self.y0+self.height/2,
                           text = self.text,font= "Arial 14 bold")

class bfsButton(metricBuilderButton): #for importing and exporting
    #init; stays the same
    def onMouse(self,event):
        for node in self.graph.nodeSet:
            if (node.inNode(event.x,event.y)):
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
        self.undirEdgeButton = edgeLegalityButton(x0 = self.edgeMakerButton.x0, 
            y0= self.edgeMakerButton.y0-self.buttonHeight,selected = False,
            width = self.buttonWidth/2,height = self.buttonHeight, text="Undir",
            assocEdgeMakerButton = self.edgeMakerButton,edgeType = "undirected")
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
        self.metricBuilderButton = metricBuilderButton(x0 = self.wikiScraperButton.x0 + 
            self.buttonWidth + self.buttonMargin, y0 = self.edgeMakerButton.y0,
            selected = False, width = self.buttonWidth, height = self.buttonHeight,
            text = "Metric Builder",graph=self.graph,reportTab = self.reportTab)

    def initiateBFSButton(self):
        self.bfsButton = bfsButton(x0 = self.metricBuilderButton.x0 + 
            self.buttonWidth + self.buttonMargin, y0 = self.edgeMakerButton.y0,
            selected = False, width = self.buttonWidth,
            height = self.buttonHeight, text = "BFS",graph=self.graph,
            reportTab = self.reportTab)

    def buttonInitiator(self): #helper to make buttons
        self.buttonWidth = 100
        self.buttonHeight =  30
        self.buttonMargin = 10 #for margin 
        self.initiateMakerButtons() #gets edge and nodemaker
        self.initiateEdgeLegalityButtons() #gets my legality buttons
        self.initiateWikiScraperButton()
        self.initiateMetricBuilderButton()
        self.initiateBFSButton()
        self.edgeMakerButton.legalityButtonList = [self.undirEdgeButton,
        self.dirEdgeButton] #needed to add this later
        self.buttonList = [self.nodeMakerButton,self.edgeMakerButton,
                self.wikiScraperButton,self.metricBuilderButton,self.bfsButton,
                self.undirEdgeButton,self.dirEdgeButton]
	
    def reportInitiator(self): #makes report tab
        tabDiv = 3
        (tabWidth,tabHeight) = (self.width/tabDiv,self.height)
        (x0,y0) = (self.width-tabWidth,0)
    	self.reportTab = reportTab(x0 = x0,y0 = y0,
            width = tabWidth, height = tabHeight,graph = self.graph,
            universalStorage = self.universalStorage,selectedItem=None)

	#actual initialization

    def onInit(self):
        self.graph = classScript.graph()
        #so other parts can reference to this
        self.universalStorage = Struct(r = 30,nodeDefaultLabelCounter = 0,
            edgeDefaultLabelCounter = 0) 
        self.reportInitiator()
        self.buttonInitiator() #helps make buttons
        self.entryActive = False
        self.link = "" #handle this later for entry
        self.entryCounter = 0
        self.bfsActive = False

    #mouse and key functions

    #helpers for mouse and key functions

    def entryReset(self): #meant for resetting particular events
        self.entryActive = False
        self.link = ""
        (self.entryCounter,self.maxEntryCounter) = (0,0)
        (self.entryList,self.entryListReq) = ([],[])

    def requirementChecker(self):
        try:
            self.link = eval(self.link)
            if type(self.link) == self.entryListReq[self.entryCounter]:
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

    def entryActiveKey(self,event):
        if (event.keysym == "Return"):
            self.requirementChecker() #checks if it satisfies our requirements
            if self.entryCounter == self.maxEntryCounter: #got all entries
                (link,depth,degree) = self.parseForWikiGraph(self.entryList)
                self.graph = ws.buildWikiGraph(link,depth,degree,
                    self.reportTab.x0,self.nodeMakerButton.y0)
                self.graph.wikiCleaner() #cleans graph after a wiki scrape
                self.reportTab.graph = self.edgeMakerButton.graph=self.nodeMakerButton.graph=self.graph
                self.wikiScraperButton.graph = self.metricBuilderButton.graph = self.bfsButton.graph = self.graph
                self.entryReset()
                self.reportTab.resetInfo()
        elif (event.keysym == "BackSpace"):
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
        else:
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
                        and type(button)==wikiScraperButton):
                        self.entryActive = True
                        self.entryText = ["Please write your starting page handle.",
                        "Please write the max depth (as an integer).",
                        "Please write the max degree (as an integer)."]
                        self.maxEntryCounter = len(self.entryText)
                        self.entryCounter = 0
                        self.entryList = []
                        self.entryListReq = [str, int, int] #requirements on entry
                        return
                    elif (button.inButton(event) and 
                        type(button) != edgeLegalityButton): 
                        givenButton = button
                        givenButton.selected = True
                        for button in self.buttonList:
                            if (button != givenButton): button.selected = False
                        for node in self.graph.nodeSet: #deselect all nodes
                            node.selected = False
                        for edge in self.graph.edgeSet: #deselect all edges
                            edge.selected = False
                        return #prevents going to commands
                for button in self.buttonList:
                    if (button.selected):
                        button.onMouse(event)

    def onMouseDrag(self,event):
        if (not(self.bfsActive)):
            if (not(self.entryActive)):
                if (self.inAnimationBounds(event)):
                    for button in self.buttonList:
                        if (button.selected): button.onMouseDrag(event)

    def onMouseRelease(self,event):
        if (not(self.bfsActive)):
            if (not(self.entryActive)):
                if (self.inAnimationBounds(event)):
                    for button in self.buttonList:
                        if (button.selected): button.onMouseRelease(event)

    def onKey(self,event):
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

    def onMouseMove(self,event):
        if (self.inAnimationBounds(event)):
            for node in self.graph.nodeSet:
                if node.inNode(event.x,event.y):
                    node.showInfo = True
                else: node.showInfo = False

    #drawing functions

    #drawing helpers

    def drawEntryActiveScreen(self,canvas):
        r = 200
        (x0,y0,x1,y1) = (self.width/2-r,self.height/2-r, self.width/2+r,
                        self.height/2+r)
        canvas.create_rectangle(x0,y0,x1,y1,fill="gray")
        canvas.create_text(self.width/2,y0,
            text=self.entryText[self.entryCounter],
            font = "Arial 14 bold", anchor="n")
        canvas.create_text(self.width/2,y0+r,text=str(self.link),
            font = "Arial 14 bold",anchor="n")

    #actual drawing functions

    def onDraw(self, canvas):
        self.graph.draw(canvas)
        if self.entryActive:
            self.drawEntryActiveScreen(canvas)
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

#running program

nodeGUI(width=1200, height=800,windowTitle = "Networks GUI",
    aboutText = "Networks GUI \n By Michael Rosenberg",
    ).run()
