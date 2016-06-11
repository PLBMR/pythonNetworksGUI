#termProject-wikiScraper.py

#imports

import classScript #gives me my classes
import urllib2
from bs4 import BeautifulSoup
import random
import time #just for testing

def makeSoup(page): #let's us parse page
    try:
        html_doc = urllib2.urlopen(page) #gets page
        soup = BeautifulSoup(html_doc) #puts page in data structure
        return soup
    except: #we have a broken link
        return None

def grabHeaderLinks(page,wikiHandle,maxDeg): #must be legal page
    listOfHeaderLinks = []
    pageSoup = makeSoup(page) #allows us to parse html of page
    if (pageSoup == None): #broken link
        return listOfHeaderLinks #empty list
    maxPageCounter = maxDeg #meant to control growth of algorithm
    bodyText = pageSoup.find("div",id="bodyContent")
    #add truth statements to prevent errors
    for linkTag in bodyText.find_all("a",title=True,href=True):
        if (len(listOfHeaderLinks) == maxPageCounter): #reached our max
            break #don't want to look at any more
        elif ("/wiki/" in linkTag["href"] and ".jpg" not in linkTag["href"]
            and ".jpeg" not in linkTag["href"] 
            and ".png" not in linkTag["href"]): 
            #goes to actual wiki page
            suffix = linkTag["href"]
            newPage = wikiHandle + suffix
            listOfHeaderLinks.append(newPage)
    return listOfHeaderLinks

#wikipedia scraper

def tryWikiScrape(startWikiNode,depth,maxDeg): #give starting wikipedia page, 
    #returns network of headers at less than or equal to the given depth:
    wikiDict = {}
    wikiHandle = "http://en.wikipedia.org"
    startWikiPage = wikiHandle + startWikiNode #assume node starts with /wiki/
    def scraper(wikiDict, startWikiPage,depth,depthCounter = 0):
        wikiDict[startWikiPage] = {}
        if (depthCounter < depth):
            listOfHeaderLinks = grabHeaderLinks(startWikiPage,wikiHandle,maxDeg)
            for link in listOfHeaderLinks:
                scraper(wikiDict[startWikiPage],link, depth, depthCounter + 1)
    scraper(wikiDict, startWikiPage, depth)
    return wikiDict

def buildWikiGraph(startWikiNode,depth,maxDeg,canvasWidth,canvasHeight):
    wikiGraph = classScript.graph()
    wikiDict = tryWikiScrape(startWikiNode,depth,maxDeg)
    wikiHandle = "http://en.wikipedia.org"
    startWikiPage = wikiHandle + startWikiNode
    #draw it randomly on the graph
    (cx,cy) = (random.uniform(0,canvasWidth),random.uniform(0,canvasHeight))
    r = 20
    givenNode = classScript.node(cx=cx,cy=cy,r=r,label=startWikiPage)
    memoizer = {givenNode.label : givenNode} #used for repeated vertices
    wikiGraph.add_node_man(givenNode)
    def builder(wikiGraph,wikiDict,givenNode):
        for linkKey in wikiDict[givenNode.label]:
            if linkKey in memoizer: #already been here
                memoizedNode = memoizer[linkKey]
                edgeLabel = str(givenNode.label)+" to "+str(memoizedNode.label)
                newEdge = classScript.edge(fromNode=givenNode,
                toNode=memoizedNode,edgeType = "directed",edgeLabel = edgeLabel,
                selected = False, weight = 1)
                wikiGraph.add_edge_man(newEdge,givenNode,memoizedNode)
            else:
                (cx,cy) = (random.uniform(0,canvasWidth),
                    random.uniform(0,canvasHeight))
                linkageNode = classScript.node(cx=cx,cy=cy,r=r,label=linkKey)
                wikiGraph.add_node_man(linkageNode)
                edgeLabel = str(givenNode.label)+" to "+str(linkageNode.label)
                newEdge = classScript.edge(fromNode=givenNode,
                toNode=linkageNode,edgeType = "directed",edgeLabel = edgeLabel,
                selected = False, weight = 1)
                wikiGraph.add_edge_man(newEdge,givenNode,linkageNode)
                memoizer[linkageNode.label] = linkageNode
                builder(wikiGraph,wikiDict[givenNode.label],linkageNode)
    builder(wikiGraph,wikiDict,givenNode)
    return wikiGraph