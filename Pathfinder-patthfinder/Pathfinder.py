import sys
from PyQt5 import QtWidgets, uic
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.Qt import Qt, QTimer
from PyQt5 import QtCore
from FrontEnd import Ui_Dialog

sys.setrecursionlimit(10**6)

global outerIter, button, ROW, COL, startPos, endPos, obstaclePos

outerIter, button = 0, 0
ROW, COL = 64, 40
startPos, endPos, obstaclePos = [-1, -1], [-1, -1], []

# defining a class node for the elements in the graphicsview
class Node():
    def __init__(self, parent = None, position = None):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0
        self.isExplored = False

    def __eq__(self, other):
        return self.position == other.position

class MainWindow(QtWidgets.QMainWindow, Ui_Dialog):

    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.createGraphicsView()

        # linking the buttons to corresponding functions
        self.startb.pressed.connect(self.startMode)
        self.endb.pressed.connect(self.endMode)
        self.obsb.pressed.connect(self.obstacleMode)
        self.visb.pressed.connect(self.visualizeMode)
        self.clrScrb.pressed.connect(self.clearScreenMode)
        self.clrObsb.pressed.connect(self.clearObstaclesMode)
        self.clrPathb.pressed.connect(self.clearPathMode)

    # Function to link mouse events of graphicsview
    def createGraphicsView(self):
        self.scene = QGraphicsScene()
        self.graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.drawGrid()
        self.graphicsView.viewport().installEventFilter(self)

    # Function to draw gridlines 
    def drawGrid(self):
        self.scene.setBackgroundBrush(Qt.darkCyan)
        for x in range(0, 1281, 20):
            self.scene.addLine(x, 0, x, 800, QPen(Qt.white))
        for y in range(0, 801, 20):
            self.scene.addLine(0, y, 1280, y, QPen(Qt.white))
        self.graphicsView.setScene(self.scene)

    # Function to check overlaps between start, end and obstable node 
    def overlapCheck(self, a, b):
        global startPos, endPos, obstaclePos
        for lst in obstaclePos:
            if lst == [a, b]:
                return True
        if startPos == [a, b]:
            return True
        elif endPos == [a, b]:
            return True
        return False

    # Function to check overlaps between obstable node and [a,b]
    def obsOverlapCheck(self, a, b):
        global obstaclePos
        for lst in obstaclePos:
            if lst == [a, b]:
                return True
        return False

    def startMode(self):
        global button
        button = 0
    def endMode(self):
        global button
        button = 1
    def obstacleMode(self):
        global button
        button = 2

    # Getting user choice for algorithm
    def visualizeMode(self):
        algo = self.algoCombo.itemText(self.algoCombo.currentIndex())
        if algo == "A* Algorithm":
            self.paintPath(self.aStarAlgo())
        elif algo == "Dijkstra\'s Algorithm":
            self.dijkstraAlgo()

    def clearScreenMode(self):
        self.scene.clear()
        global startPos, endPos, obstaclePos
        startPos = [-1, -1]
        endPos = [-1, -1]
        obstaclePos = []
        self.drawGrid()
    def clearPathMode(self):
        self.scene.clear()
        global obstaclePos

        self.drawGrid()
        brush = QBrush()
        brush.setColor(Qt.red)
        brush.setStyle(Qt.SolidPattern)
        borderColor = Qt.black
        if not startPos[0] == -1:
            self.scene.addRect(QRectF(startPos[0] * 20, startPos[1] * 20, 20, 20), borderColor, brush)
        if not endPos[0] == -1:
            brush.setColor(Qt.green)
            self.scene.addRect(QRectF(endPos[0] * 20, endPos[1] * 20, 20, 20), borderColor, brush)

        brush.setColor(Qt.gray)
        borderColor = Qt.black
        for i in obstaclePos:
            self.scene.addRect(QRectF(i[0] * 20, i[1] * 20, 20, 20), borderColor, brush)
    def clearObstaclesMode(self):
        self.scene.clear()
        global obstaclePos
        obstaclePos = []

        self.drawGrid()
        brush = QBrush()
        brush.setColor(Qt.red)
        brush.setStyle(Qt.SolidPattern)
        borderColor = Qt.black
        if not startPos[0] == -1:
            self.scene.addRect(QRectF(startPos[0] * 20, startPos[1] * 20, 20, 20), borderColor, brush)
        if not endPos[0] == -1:
            brush.setColor(Qt.green)
            self.scene.addRect(QRectF(endPos[0] * 20, endPos[1] * 20, 20, 20), borderColor, brush)

    # Function to calculate Manhattan distance between the 2 nodes
    def nodeDist(self, node1, node2):
        return abs(node1.position[0] - node2.position[0]) + abs(node1.position[1] - node2.position[1])

    # Function to paint the path for A star 
    def paintPath(self, path):
        brush = QBrush()
        brush.setColor(Qt.black)
        brush.setStyle(Qt.SolidPattern)
        borderColor = Qt.black
        if path == None:
            print("NO PATH EXISTS!!!")
        else:
            for i in path[1:-1]:
                self.scene.addRect(QRectF(i[0] * 20, i[1] * 20, 20, 20), borderColor, brush)
    # A Star algorithm
    def aStarAlgo(self):
        global startPos, endPos, path, outerIter
        maxIter = 10**6

        if startPos[0] != -1 and endPos != -1:

            startNode = Node(None, startPos)
            endNode = Node(None, endPos)
            
            openList = []   # Nodes which aren't visited yet
            closeList = []  # Nodes which are already visited
            openList.append(startNode)

            movement = [[-1, 0], [0, -1], [1, 0], [0, 1]]

            while len(openList) > 0:

                cont = 0
                currNode = openList[0]
                currIndex = 0

                for index, item in enumerate(openList):
                    outerIter += 1
                    if item.f < currNode.f:
                        currNode = item
                        currIndex = index
                    if currNode.position != startPos and currNode.position != endPos:
                        brush = QBrush()
                        brush.setColor(Qt.cyan)
                        brush.setStyle(Qt.SolidPattern)
                        borderColor = Qt.black
                        self.scene.addRect(QRectF(currNode.position[0] * 20, currNode.position[1] * 20, 20, 20), borderColor, brush)

                QApplication.processEvents()

                if outerIter >= maxIter:
                    print("Too many iterations.")
                    path = []
                    return path

                # Removing the Current node from the open list and adding it to closelist
                openList.pop(currIndex)
                closeList.append(currNode)

                if currNode == endNode:
                    path = []
                    current = currNode

                    while current is not None:
                        path.append(current.position)
                        current = current.parent
                    return path[::-1]

                children = []

                for move in movement:
                    nodePos = [currNode.position[0] + move[0], currNode.position[1] + move[1]]

                    if nodePos[0] > ROW - 1 or nodePos[0] < 0 or nodePos[1] > COL - 1 or nodePos[1] < 0:
                        continue

                    if Node(currNode, nodePos) in closeList:
                        continue

                    if self.obsOverlapCheck(nodePos[0], nodePos[1]):
                        continue

                    newNode = Node(currNode, nodePos)
                    children.append(newNode)

                for child in children:
                    for closeChild in closeList:
                        if child == closeChild:
                            cont = 1

                    if cont == 1:
                        cont = 0
                        continue


                    # The g cost is added by 1 
                    child.g = currNode.g +  1
                    child.h = self.nodeDist(endNode, child)
                    child.f = child.g + child.h

                    for openNode in openList:
                        if child == openNode and child.g >= openNode.g:
                            cont = 1

                    if cont == 1:
                        cont = 0
                        continue

                    openList.append(child)

    # Dijkstra Algorithm
    def dijkstraAlgo(self):

        R = [[0 for i in range(64 * 40)] for j in range(40 * 64)]

        # Converting to an array
        x = int(endPos[1])
        y = int(endPos[0])
        dest = x * 64 + y

        x = int(startPos[1])
        y = int(startPos[0])
        src = x * 64 + y

        # Initializing elements of a 64 x 40 Matrix with 1  
        self.maze = [[1 for i in range(64)] for j in range(40)]


        # Substituting obstacle nodes with 0
        for node in obstaclePos:
            self.maze[node[1]][node[0]] = 0

        for i in range(64 * 40):
            if (self.maze[int(i / 64)][i % 64]):
                
                # Checking for edge cases and if the neighbour is not an obstacle
                    # and updating the R matrix 

                if i - 1 >= (int)(i / 64) * 64 and (self.maze[int((i - 1) / 64)][(i - 1) % 64]): 
                    R[i][i - 1] = self.maze[int((i - 1) / 64)][(i - 1) % 64]

                if (i + 1) < ((int)(i / 64) + 1) * 64 and (self.maze[int((i + 1) / 64)][(i + 1) % 64]):
                    R[i][i + 1] = self.maze[int((i + 1) / 64)][(i + 1) % 64]

                if (i - 64) >= 0 and (self.maze[int((i - 64) / 64)][(i - 64) % 64]):
                    R[i][i - 64] = self.maze[int((i - 64) / 64)][(i - 64) % 64]

                if (i + 64) < 40 * 64 and (self.maze[int((i + 64) / 64)][(i + 64) % 64]):
                    R[i][i + 64] = self.maze[int((i + 64) / 64)][(i + 64) % 64]

    
        openList = set()          # Nodes yet to be visited
        openList.add((0, src))    
        parentNode = {}             

        dist = {i: float("inf") for i in range(64 * 40)}   # Initialzinf distance to infinity
        dist[src] = 0
        openListHash = {src}

        while len(openList):

            current = openList.pop()[1]
            if current != dest and current != src:
                self.scene.addRect(QRectF((current % 64) * 20, (int)(current / 64) * 20, 20, 20), Qt.black, Qt.cyan)
                QApplication.processEvents()
            openListHash.remove(current)

            if current == dest:
                brush = QBrush()
                brush.setStyle(Qt.SolidPattern)
                borderColor = Qt.black
                brush.setColor(Qt.black)
                while current in parentNode:
                    current = parentNode[current]
                    if current != src:
                        self.scene.addRect(QRectF((current % 64) * 20, (int)(current / 64) * 20, 20, 20), Qt.black, Qt.black)
                return

            for neighbor in range(64 * 40):

                if R[current][neighbor]:
                    tempDist = dist[current] + R[current][neighbor]      

                    # Checking the distance of neighbours
                    if tempDist < dist[neighbor]:

                        # Removing already visited neighbours
                        if neighbor in openListHash:
                            openList.remove((dist[neighbor], neighbor))
                            openListHash.remove(neighbor)

                        # Assigning the new shorter temp dist
                        dist[neighbor] = tempDist

                        # Appending the current node to parent
                        parentNode[neighbor] = current

                        # adding 
                        openList.add((dist[neighbor], neighbor))
                        openListHash.add(neighbor)


        print("NO PATH EXISTS!!!")
        return False
   
   
    def eventFilter(self, source, event):
        clrBrush = QBrush()
        clrBrush.setColor(Qt.darkCyan)
        clrBrush.setStyle(Qt.SolidPattern)
        clrBorderColor = Qt.white
        borderColor = Qt.black

        if (event.type() == QtCore.QEvent.MouseMove and source is self.graphicsView.viewport()):

            # Getting coords of obstacle nodes while clicking and dragging the left mouse button 
            if button == 2:
                pos = event.pos()
                brush = QBrush()
                brush.setColor(Qt.gray)
                brush.setStyle(Qt.SolidPattern)
                x = (pos.x() // 20)
                y = (pos.y() // 20)
                if not self.overlapCheck(x, y) and x < 64 and y < 40 and x >= 0 and y >= 0:
                    self.scene.addRect(QRectF(x * 20, y * 20, 20, 20), borderColor, brush)
                    obstaclePos.append([x, y])

        if (event.type() == QtCore.QEvent.MouseButtonPress and source is self.graphicsView.viewport()):

            # Getting coords of start node while clicking left mouse button 
            if button == 0:
                pos = event.pos()
                brush = QBrush()
                brush.setColor(Qt.red)
                brush.setStyle(Qt.SolidPattern)
                x = (pos.x() // 20)
                y = (pos.y() // 20)
                if not self.overlapCheck(x, y) and x < 64 and y < 40 and x >= 0 and y >= 0:
                    self.scene.addRect(QRectF(x * 20, y * 20, 20, 20), borderColor, brush)

                    # clearing the old start node if there exists one 
                    if not startPos[0] == -1:
                        self.scene.addRect(QRectF(startPos[0] * 20, startPos[1] * 20, 20, 20), clrBorderColor, clrBrush)
                    startPos[0] = x
                    startPos[1] = y

            # Getting coords of end node while clicking left mouse button 
            elif button == 1:
                pos = event.pos()
                brush = QBrush()
                brush.setColor(Qt.green)
                brush.setStyle(Qt.SolidPattern)
                x = (pos.x() // 20)
                y = (pos.y() // 20)
                if not self.overlapCheck(x, y) and x < 64 and y < 40 and x >= 0 and y >= 0:
                    self.scene.addRect(QRectF(x * 20, y * 20, 20, 20), borderColor, brush)

                    # clearing the old end node if there exists one 
                    if not endPos[0] == -1:
                        self.scene.addRect(QRectF(endPos[0] * 20, endPos[1] * 20, 20, 20), clrBorderColor, clrBrush)
                    endPos[0] = x
                    endPos[1] = y

            # Getting coords of obstacle nodes while clicking the left mouse button 
            elif button == 2:
                pos = event.pos()
                brush = QBrush()
                brush.setColor(Qt.gray)
                brush.setStyle(Qt.SolidPattern)
                x = (pos.x() // 20)
                y = (pos.y() // 20)
                if not self.overlapCheck(x, y) and x < 64 and y < 40 and x >= 0 and y >= 0:
                    self.scene.addRect(QRectF(x * 20, y * 20, 20, 20), borderColor, brush)
                    obstaclePos.append([x, y])

        return QtWidgets.QWidget.eventFilter(self, source, event)



app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec_())

