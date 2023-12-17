from cmu_graphics import *
from grid import *
from PIL import Image
import os, pathlib, random
# ^Imported and used for game functionality

#-------------------------------------------------------------------------------
# Building class 
 
class Building:
    def __init__(self):
        cw,ch = app.center   
        self.buttons = [Button(cw/2+70,ch+250,50,20,0,'Delete',None)]
        self.buttonActions = ['delete']

    
    # button draw function for all buildings
    def drawButtons(self): 
        for button in self.buttons:
            button.draw()

    # default function for all buildings
    def draw(self,app,row,col):
        x,y = findGridCenter(app,row,col)
        drawImage(CMUImage(self.image),x,y,width=app.tileHeight,height=app.tileHeight)

# Residential class as a Building
class Residential(Building):
    def __init__(self):
        super().__init__()
        self.level = 0
        self.level = 0
        self.population = 100 # Houses a default population of 100 
        self.imageFiles = ["images/house_lv0.png"]
        self.image = openImage(self.imageFiles[0])
        self.imageWidth,self.imageHeight = self.image.width,self.image.height
        self.happiness = 100

    def __repr__(self):
        return f'Level {self.level} house'
    
    # Calculates happiness based on grid proximity to other building types 
    def findHappiness(self,app,row,col): 
        utilityFound = False
        industryFound = False
        municipalFound = False
        gridConnected = False
        for nRow in range(app.boardRows):
            for nCol in range(app.boardCols):
                gridBuilding = app.board[nRow][nCol]
                if isinstance(gridBuilding,Utility):
                    distance = abs(row-nRow)+abs(col-nCol)
                    distFactor = 1-distance/(app.boardRows+app.boardCols)
                    utilityFound = True if distFactor > 0.7 else False
                if isinstance(gridBuilding,Industry):
                    distance = abs(row-nRow)+abs(col-nCol)
                    distFactor = 1-distance/(app.boardRows+app.boardCols)
                    industryFound = True if (distFactor > 0.7) else False
                if isinstance(gridBuilding,Municipal):
                    distance = abs(row-nRow)+abs(col-nCol)
                    distFactor = 1-distance/(app.boardRows+app.boardCols)
                    municipalFound = True if (distFactor > 0.7) else False
        if col != 0 and isinstance(app.board[row][col-1],Road):
            gridConnected = True if checkGridPower(row,col-1) else gridConnected
        if col != app.boardCols and isinstance(app.board[row][col+1],Road):
            gridConnected = True if checkGridPower(row,col-1) else gridConnected
        if row != app.boardRows and isinstance(app.board[row+1][col],Road):
            gridConnected = True if checkGridPower(row,col-1) else gridConnected
        if row != 0 and isinstance(app.board[row-1][col],Road):
            gridConnected = True if checkGridPower(row,col-1) else gridConnected
        
        changeIntensity = (1 - self.happiness/120) * 5
        connectionFactor = 2
        if gridConnected == True: 
            connectionFactor = 1
        for factor in [utilityFound,industryFound,municipalFound]:
            if factor == False:
                self.happiness -= changeIntensity * connectionFactor
            else: 
                self.happiness += changeIntensity * connectionFactor
        self.happiness = 0 if self.happiness < 0 else self.happiness
        self.happiness = 100 if self.happiness > 100 else self.happiness
        return self.happiness

def checkGridPower(row,col):
    for grid in app.powerGrids:
        if (row,col) in grid.roadGrids:
            return True

# House class as a Residential Building   
class House(Residential):
    def __init__(self):
        super().__init__()
        self.imageFiles = ["images/house_lv0.png","images/house_lv1.png",
                           "images/house_lv2.png"]
        self.image = openImage(self.imageFiles[0])
        self.imageWidth,self.imageHeight = self.image.width,self.image.height
        cw,ch = app.center   
        self.buttons = [Button(cw/2+70,ch+250,50,20,0,'Delete',None)]
        self.buttonActions = ['delete']
        self.cost = 1000
        self.energyCost = 10
                                
    def levelUp(self):
        if self.level < 2:
            self.level += 1
            self.image = openImage(self.imageFiles[self.level])
            self.population += 100 

# Apartment class as a Residential Building   
class Apartment(Residential):
    def __init__(self):
        super().__init__()
        self.imageFiles = ["images/apartment.png"]
        self.image = openImage(self.imageFiles[0])
        self.imageWidth,self.imageHeight = self.image.width,self.image.height
        self.population = 200
        self.cost = 2000
        self.energyCost = 20


# Road Class as a Building
class Road(Building):
    def __init__(self,app,row,col,direction='default'):
        super().__init__()
        self.direction = direction
        self.connectedNorth = False
        self.connectedSouth = False
        self.connectedEast = False
        self.connectedWest = False
        self.updateConnections(app,row,col)
        self.updateDirection
        self.cost = 100

    # Draws road based on directionality
    def draw(self,app,row,col):
        if self.direction == 'all':
            drawRoadAll(app,row,col)
        elif self.direction == 'north-south':
            drawRoadNorthSouth(app,row,col)
        elif self.direction == 'north-south-east':
            drawRoadNSE(app,row,col)
        elif self.direction == 'north-south-west':
            drawRoadNSW(app,row,col)
        elif self.direction == 'north-east-west':
            drawRoadNEW(app,row,col)
        elif self.direction == 'south-east-west':
            drawRoadSEW(app,row,col)
        elif self.direction == 'south-west':
            drawRoadSW(app,row,col)
        elif self.direction == 'south-east':
            drawRoadSE(app,row,col)
        elif self.direction == 'north-east':
            drawRoadNE(app,row,col)
        elif self.direction == 'north-west':
            drawRoadNW(app,row,col)
        elif self.direction == 'east-west':
            drawRoadEastWest(app,row,col)
        elif self.connectedNorth or self.connectedSouth:
            drawRoadNorthSouth(app,row,col)
        elif self.connectedEast or self.connectedWest:
            drawRoadEastWest(app,row,col)
        else:
            drawRoadNorthSouth(app,row,col)

    # Checks adjacent grids for roads
    def updateConnections(self,app,row,col):
        if col != 0 and isinstance(app.board[row][col-1],Road):
            self.connectedNorth = True
        else:             
            self.connectedNorth = False
        if col != 0 and isinstance(app.board[row][col+1],Road):
            self.connectedSouth = True
        else:
            self.connectedSouth = False
        if row != 0 and isinstance(app.board[row+1][col],Road):
            self.connectedEast = True
        else:
            self.connectedEast = False
        if row != 0 and isinstance(app.board[row-1][col],Road):
            self.connectedWest = True
        else:
            self.connectedWest = False
        self.updateDirection()

    # Updates road direction based on existence of adjacent roads
    def updateDirection(self):
        if (self.connectedNorth and self.connectedSouth and 
            self.connectedEast and self.connectedWest):
            self.direction = 'all'
        elif (self.connectedNorth and self.connectedSouth and
              self.connectedEast):
            self.direction = 'north-south-east'
        elif (self.connectedNorth and self.connectedSouth and
              self.connectedWest):
            self.direction = 'north-south-west'
        elif (self.connectedNorth and self.connectedEast and
              self.connectedWest):
            self.direction = 'north-east-west'
        elif (self.connectedSouth and self.connectedEast and
              self.connectedWest):
            self.direction = 'south-east-west'
        elif self.connectedNorth and self.connectedSouth:
            self.direction = 'north-south'
        elif self.connectedNorth and self.connectedEast:
            self.direction = 'north-east'
        elif self.connectedNorth and self.connectedWest:
            self.direction = 'north-west'
        elif self.connectedSouth and self.connectedEast:
            self.direction = 'south-east'
        elif self.connectedSouth and self.connectedWest:
            self.direction = 'south-west' 
        elif self.connectedEast and self.connectedWest:
            self.direction = 'east-west'
#-------------------------------------------------------------------------------
# Draw functions for each possible road iteration

def drawRoadAll(app,row,col):
    x,y = calcCoords(app,row,col)
    edgeW = app.tileWidth/10
    edgeH = app.tileHeight/10
    drawPolygon(x+edgeW,y+edgeH,x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf-edgeH,
                x-edgeW,y+app.tileHeight-edgeH,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf+edgeH,fill='black')
    drawPolygon(x-edgeW,y+edgeH,x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf+edgeH,
                x+edgeW,y+app.tileHeight-edgeH,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf-edgeH,fill='black')
    drawLine(x+app.tileWidth/4,y+app.tileHeight/4,x-app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')
    drawLine(x-app.tileWidth/4,y+app.tileHeight/4,x+app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')
def drawRoadNorthSouth(app,row,col): 
    x,y = calcCoords(app,row,col)
    edgeW = app.tileWidth/10
    edgeH = app.tileHeight/10
    drawPolygon(x+edgeW,y+edgeH,x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf-edgeH,
                x-edgeW,y+app.tileHeight-edgeH,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf+edgeH,fill='black')
    drawLine(x+app.tileWidth/4,y+app.tileHeight/4,x-app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')
def drawRoadEastWest(app,row,col):
    x,y = calcCoords(app,row,col)
    edgeW = app.tileWidth/10
    edgeH = app.tileHeight/10
    drawPolygon(x-edgeW,y+edgeH,x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf+edgeH,
                x+edgeW,y+app.tileHeight-edgeH,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf-edgeH,fill='black')
    drawLine(x-app.tileWidth/4,y+app.tileHeight/4,x+app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')
def drawRoadNSE(app,row,col):
    x,y = calcCoords(app,row,col)
    edgeW = app.tileWidth/10
    edgeH = app.tileHeight/10
    drawPolygon(x+edgeW,y+edgeH,
                x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf-edgeH,
                x+app.tileWidthHalf-edgeW*2,y+app.tileHeightHalf,
                x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf+edgeH,
                x+edgeW,y+app.tileHeight-edgeH,
                x,y+app.tileHeight-edgeH*2,
                x-edgeW,y+app.tileHeight-edgeH,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf+edgeH,
                fill='black')
    drawLine(x+app.tileWidth/4,y+app.tileHeight/4,x-app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')
    drawLine(x,y+app.tileHeight/2,x+app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')   
def drawRoadNSW(app,row,col):
    x,y = calcCoords(app,row,col)
    edgeW = app.tileWidth/10
    edgeH = app.tileHeight/10
    drawPolygon(x+edgeW,y+edgeH,
                x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf-edgeH,
                x-edgeW,y+app.tileHeight-edgeH,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf+edgeH,
                x-app.tileWidthHalf+edgeW*2,y+app.tileHeightHalf,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf-edgeH,
                x-edgeW,y+edgeH,
                x,y+edgeH*2,fill='black')
    drawLine(x+app.tileWidth/4,y+app.tileHeight/4,x-app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')
    drawLine(x,y+app.tileHeight/2,x-app.tileWidth/4,y+app.tileHeight*1/4,
                dashes=True,fill='yellow')
def drawRoadNEW(app,row,col):
    x,y = calcCoords(app,row,col)
    edgeW = app.tileWidth/10
    edgeH = app.tileHeight/10
    drawPolygon(x+edgeW,y+edgeH,
                x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf-edgeH,
                x+app.tileWidthHalf-edgeW*2,y+app.tileHeightHalf,
                x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf+edgeH,
                x+edgeW,y+app.tileHeight-edgeH,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf-edgeH,
                x-edgeW,y+edgeH,
                x,y+edgeH*2, fill='black')
    drawLine(x-app.tileWidth/4,y+app.tileHeight/4,x+app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')
    drawLine(x,y+app.tileHeightHalf,x+app.tileWidth/4,y+app.tileHeight*1/4,
                dashes=True,fill='yellow')
def drawRoadSEW(app,row,col):
    x,y = calcCoords(app,row,col)
    edgeW = app.tileWidth/10
    edgeH = app.tileHeight/10
    drawPolygon(x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf+edgeH,
                x+edgeW,y+app.tileHeight-edgeH,
                x,y+app.tileHeight-edgeH*2,
                x-edgeW,y+app.tileHeight-edgeH,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf+edgeH,
                x-app.tileWidthHalf+edgeW*2,y+app.tileHeightHalf,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf-edgeH,
                x-edgeW,y+edgeH, fill='black')
    drawLine(x-app.tileWidth/4,y+app.tileHeight/4,x+app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')
    drawLine(x,y+app.tileHeightHalf,x-app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')
def drawRoadNE(app,row,col):
    x,y = calcCoords(app,row,col)
    edgeW = app.tileWidth/10
    edgeH = app.tileHeight/10
    drawPolygon(x+edgeW,y+edgeH,
                x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf-edgeH,
                x+app.tileWidthHalf-edgeW*2,y+app.tileHeightHalf,
                x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf+edgeH,
                x+edgeW,y+app.tileHeight-edgeH,
                x-app.tileWidthHalf+edgeW*2,y+app.tileHeightHalf
                ,fill='black')
    drawLine(x,y+app.tileHeightHalf,x+app.tileWidth/4,y+app.tileHeight*1/4,
                dashes=True,fill='yellow')
    drawLine(x,y+app.tileHeightHalf,x+app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')
def drawRoadSE(app,row,col):
    x,y = calcCoords(app,row,col)
    edgeW = app.tileWidth/10
    edgeH = app.tileHeight/10
    drawPolygon(x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf+edgeH,
                x+edgeW,y+app.tileHeight-edgeH,
                x,y+app.tileHeight-edgeH*2,
                x-edgeW,y+app.tileHeight-edgeH,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf+edgeH,
                x,y+edgeH*2, fill='black')
    drawLine(x,y+app.tileHeightHalf,x+app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')
    drawLine(x,y+app.tileHeightHalf,x-app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')
def drawRoadNW(app,row,col):
    x,y = calcCoords(app,row,col)
    edgeW = app.tileWidth/10
    edgeH = app.tileHeight/10
    drawPolygon(x+edgeW,y+edgeH,
                x+app.tileWidthHalf-edgeW,y+app.tileHeightHalf-edgeH,
                x,y+app.tileHeight-edgeH*2,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf-edgeH,
                x-edgeW,y+edgeH,
                x,y+edgeH*2,fill='black')
    drawLine(x,y+app.tileHeightHalf,x+app.tileWidth/4,y+app.tileHeight*1/4,
                dashes=True,fill='yellow')
    drawLine(x,y+app.tileHeightHalf,x-app.tileWidth/4,y+app.tileHeight*1/4,
                dashes=True,fill='yellow')
def drawRoadSW(app,row,col):
    x,y = calcCoords(app,row,col)
    edgeW = app.tileWidth/10
    edgeH = app.tileHeight/10
    drawPolygon(x+app.tileWidthHalf-edgeW*2,y+app.tileHeightHalf,
                x-edgeW,y+app.tileHeight-edgeH,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf+edgeH,
                x-app.tileWidthHalf+edgeW*2,y+app.tileHeightHalf,
                x-app.tileWidthHalf+edgeW,y+app.tileHeightHalf-edgeH,
                x-edgeW,y+edgeH, fill='black')
    drawLine(x,y+app.tileHeightHalf,x-app.tileWidth/4,y+app.tileHeight*1/4,
                dashes=True,fill='yellow')
    drawLine(x,y+app.tileHeightHalf,x-app.tileWidth/4,y+app.tileHeight*3/4,
                dashes=True,fill='yellow')

#-------------------------------------------------------------------------------
# Remaining Building Classes

# Utility class as a Building subclass
class Utility(Building):
    def __init__(self):
        super().__init__()

#Powerplant as a Utility Building
class Powerplant(Utility):
    def __init__(self):
        super().__init__()
        self.imageFiles = ["images/powerplant.png"]
        self.image = openImage(self.imageFiles[0])
        self.imageWidth,self.imageHeight = self.image.width,self.image.height
        self.cost = 2000
        self.managementCost = 200
        self.powerOutput = 100
        self.connections = 0

class PowerGrid:
    def __init__(self,source,row,col):
        self.origin = row,col
        self.roadGrids = set()
        self.powerSources = [source] 
        self.powerTotal = source.powerOutput
        self.powerConsumers = []        
        self.powerCounsumptionTotal = 0 
        
    def updatePower(self):
        self.powerTotal = 0  
        self.powerConsumptionTotal = 0
        for source in self.powerSources:
            self.powerTotal += source.powerOutput
        for consumer in self.powerConsumers:
            self.powerConsumptionTotal += consumer.powerConsumption

    def updateRoads(self,app,row,col):
        for x,y in [(1,0),(-1,0),(0,-1),(0,1)]:
            self.roadGrids = self.roadGrids|cRoads(app.board,row+x,col+y,set())

    def updateHouses(self,app):
        self.powerConsumers = []
        for row,col in self.roadGrids:
            if col != 0 and isinstance(app.board[row][col-1],Residential):
                self.powerConsumers.append(app.board[row][col-1])
            if col != app.boardCols and isinstance(app.board[row][col+1],Residential):
                self.powerConsumers.append(app.board[row][col+1])
            if row != app.boardRows and isinstance(app.board[row+1][col],Residential):
                self.powerConsumers.append(app.board[row+1][col])
            if row != 0 and isinstance(app.board[row-1][col],Residential):
                self.powerConsumers.append(app.board[row+1][col])

    def updatePowerConsumption(self):
        self.powerCounsumptionTotal = 0 
        for consumer in self.powerConsumers:
            self.powerCounsumptionTotal += consumer.energyCost              

def cRoads(board,row,col,visited):
    if (row < 0 or row >= len(board) or col < 0 or col >= len(board[0])):
        return visited
    if (row,col) in visited:
        return visited
    if not isinstance(board[row][col],Road):
        return visited
    visited.add((row,col)) 
    visited.union(cRoads(board,row+1,col,visited))
    visited.union(cRoads(board,row-1,col,visited))
    visited.union(cRoads(board,row,col+1,visited))
    visited.union(cRoads(board,row,col-1,visited))
    return visited

#Industry as a Building subclass
class Industry(Building):
    def __init__(self):
        super().__init__()
        
# Factory as a Industry Building
class Factory(Industry):
    def __init__(self):
        super().__init__()
        self.imageFiles = ["images/factory.png"]
        self.image = openImage(self.imageFiles[0])
        self.imageWidth,self.imageHeight = self.image.width,self.image.height
        self.cost = 1500
        self.incomePerPopulation = 10
        self.managementCost = 200


# Municipal as a Building subclass
class Municipal(Building):
    def __init__(self):
        super().__init__()

# Police as a Municipal Building
class Police(Municipal):
    def __init__(self):
        super().__init__()
        self.imageFiles = ["images/police_station.png"]
        self.image = openImage(self.imageFiles[0])
        self.imageWidth,self.imageHeight = self.image.width,self.image.height
        self.cost = 1500
        self.managementCost = 200


# Hospital as a Municipal Building
class Hospital(Municipal):
    def __init__(self):
        super().__init__()
        self.imageFiles = ["images/hospital.png"]
        self.image = openImage(self.imageFiles[0])
        self.imageWidth,self.imageHeight = self.image.width,self.image.height
        self.cost = 1500
        self.managementCost = 200

#-------------------------------------------------------------------------------
# Zone defines a group of grids that randomly generates buildings that are the
# same as the zone building type
class Zone:
    def __init__(self,row,col,width,height,buildingType,grids):
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.buildingType = buildingType
        self.grids = grids
        self.day = 0
        self.growthCapDay = 10
        if self.buildingType == House:
            self.color = 'yellow'
        elif self.buildingType == Apartment:
            self.color = 'pink'
    
    # Randomly places buildings within the Zone
    def grow(self):
        for row,col in self.grids:
            random.seed
            potential = maxBuildPotential(app,row,col,self.buildingType)
            potential = potential * (self.day + 1) / self.growthCapDay
            if app.board[row][col]==None and random.random()<potential:
                app.board[row][col] = self.buildingType()
                app.player.population += app.board[row][col].population
        self.day += 1 

#-------------------------------------------------------------------------------
# Button class as a template for buttons
class Button:
    def __init__(self,x,y,w,h,index,label,icon,description=None):
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self.index = index
        self.label = label
        self.description = label if description == None else description
        self.icon = openImage(icon) if isinstance(icon,str) else None

    # draws button
    def draw(self):
        drawRect(self.x,self.y,self.width,self.height,fill='white',border='gold')
        if self.icon != None:
            drawImage(CMUImage(self.icon),self.x+2,self.y+2,width=self.height-4,height=self.height-4)
        if self.icon == None:
            drawLabel(self.label,self.x+self.width/2,self.y+self.height/2,align='center')
        else:
            drawLabel(self.label,self.x+self.height,self.y+self.height/2,align='left')
    
    # checks if button is pressed
    def isPressed(self,mouseX,mouseY):
        if (mouseX > self.x and mouseX < self.x + self.width 
            and mouseY > self.y and mouseY < self.y + self.height):
            return True
        return False
        
    # does stored action
    def action(self,app,action):
        if app.isGridSelected != True:
            return
        if action == 'delete':
            row,col = app.gridSelected
            if isinstance(app.board[row][col],Residential):
                app.player.population -= app.board[row][col].population  
            if app.board[row][col] != None:
                app.player.money += app.board[row][col].cost*0.25   
            app.board[row][col] = None
            return
        # elif action == 'upgrade':
        #     row,col = app.gridSelected
        #     if isinstance(app.board[row][col],House):
        #         app.board[row][col].levelUp
        #         app.player.population += 100
        #     return
        if len(app.toggledGrids) == 1:
            singleBuild(app,action)
            return
        zone(app,action)


#-------------------------------------------------------------------------------
# Button Functions
              
# Builds single Building based on action
def singleBuild(app,action):
    row,col = app.gridSelected
    if action == 'not_implemented':
        app.notImplementedYet = True
        app.displayTimer = 300
        return
    if action == 'build_road':
        if app.isGridSelected:
            row,col = app.gridSelected
            if app.board[row][col] == None:
                if app.player.money >= Road(app,row,col).cost:
                    app.board[row][col] = Road(app,row,col)
                    app.player.money -= app.board[row][col].cost
                    for grid in app.powerGrids:
                        x,y = grid.origin
                        grid.updateRoads(app,x,y)
                        grid.updateHouses(app)
                else:
                    app.notEnoughMoney = True
    if app.board[row][col] != None:
        return
    if app.boardElevation[row][col] <= 1:
        app.invalidBuildAttempt = True
        return
    if action == 'build_house':
        if app.player.money >= House().cost:
            app.board[row][col] = House()
            for grid in app.powerGrids:
                grid.updateHouses(app)
        else:
            app.notEnoughMoney = True
    elif action == 'build_apartment':
        if app.player.money >= Apartment().cost:
            app.board[row][col] = Apartment()
        else:
            app.notEnoughMoney = True
    elif action == 'build_factory':
        if app.player.money >= Factory().cost:
            app.board[row][col] = Factory()
            app.factories.append(app.board[row][col])
        else:
            app.notEnoughMoney = True
    elif action == 'build_hospital': 
        if app.player.money >= Hospital().cost:
            app.board[row][col] = Hospital()
        else:
            app.notEnoughMoney = True
    elif action == 'build_powerplant':   
        if app.player.money >= Powerplant().cost:
            app.board[row][col] = Powerplant()
            app.board[row][col].connections = connectedPowerGrids(app,row,col)
            if app.board[row][col].connections == []:
                app.powerGrids.append(PowerGrid(app.board[row][col],row,col))
                app.powerGrids[0].updateRoads(app,row,col)
            else: 
                for grid in app.board[row][col].connections:
                    grid.powerSources += app.board[row][col]
                    grid.updateRoads(app,row,col)
                    grid.updateHouses(app)
        else:
            app.notEnoughMoney = True
    elif action == 'build_police':
        if app.player.money >= Police().cost:
            app.board[row][col] = Police()
        else:
            app.notEnoughMoney = True
    if isinstance(app.board[row][col],Residential):
        app.player.population += app.board[row][col].population
    if isinstance(app.board[row][col],Building):
        app.player.money -= app.board[row][col].cost

# Mass builds based on toggled grids
def zone(app,action):
    if action == 'build_house':
        type = House
        cost = 10
    elif action == 'build_apartment':
        type = Apartment
        cost = 20
    else:
        return
    oRow,oCol = app.gridSelected
    nRow,nCol = app.gridMouseReleased
    width = max(nRow,oRow)-min(nRow,oRow)+1
    height = max(nCol,oCol)-min(nCol,oCol)+1
    grids = getGridsSet(min(nRow,oRow),min(nCol,oCol),width,height)-app.waterGrids
    cost = len(grids)*cost
    if app.player.money < cost:
        app.notEnoughMoney = True
        return
    app.zones.append(Zone(min(nRow,oRow),min(nCol,oCol),
                          width,height,type,grids))
    app.player.money -= cost
    
# loads all buttons at appStart
def loadButtons(app):
    cw,ch = app.center
    cw -= 75
    ch -= 80
    mw = 140
    mh = 60
    app.menuButtons = [Button(cw,ch-90,150,50,0,'Continue','images/logo.png'),
                       Button(cw,ch-30,150,50,1,'New Game','images/logo.png'),
                       Button(cw,ch+30,150,50,2,'Description','images/logo.png'),
                       Button(cw,ch+90,150,50,3,'Credits','images/logo.png')]
    app.mainButtons = [Button(10,60,120,50,0,'Residential','images/house_lv0.png'),
                       Button(10,120,120,50,1 ,'Industry','symbols/money.png'),
                       Button(10,180,120,50,2,'Utilities','symbols/lightning.png'),
                       Button(10,240,120,50,3,'Municipal','symbols/siren.png'),
                       Button(10,300,120,50,4,'Roads','symbols/road.png'),
                       Button(10,360,120,50,5,'Menu','images/house_lv4.png')]
    app.buildingBtns = [Button(mw,mh*1,120,50,0,'House','images/house_lv0.png',
                               [f'Price: {House().cost}','Zone: 10/grid','Pop: 100']),       
                        Button(mw,mh*2,120,50,1,'Apartment','images/apartment.png',
                               [f'Price: {Apartment().cost}','Zone: 15/grid','Pop: 200']),
                        Button(mw,mh*3,120,50,2,'to be added',None)]
    app.industryBtns = [Button(mw,mh*1,120,50,0,'Industrial','images/factory.png',
                               [f'Price: {Factory().cost}','Money/pop: 10','Management: 200']),
                        Button(mw,mh*2,120,50,1,'Office','images/house_lv0.png'),
                        Button(mw,mh*3,120,50,2,'Commercial - to be added',None)]
    app.utilitiesBtns = [Button(mw,mh*1,120,50,0,'Heating',None),
                         Button(mw,mh*2,120,50,1,'Electricity','images/powerplant.png',
                                [f'Price: {Powerplant().cost}','Energy: 100MW']),
                         Button(mw,mh*3,120,50,2,'Water',None)]
    app.municipalBtns = [Button(mw,mh*1,120,50,0,'Hospital','images/hospital.png',
                                f'Price: {Hospital().cost}'),
                         Button(mw,mh*2,120,50,1,'Police','images/police_station.png',
                                f'Price: {Police().cost}'),
                         Button(mw,mh*3,120,50,2,'Fire Dept.',None),
                         Button(mw,mh*4,120,50,3,'Park',None),
                         Button(mw,mh*5,120,50,4,'Court House',None)]
    app.roadBtns = [Button(mw,mh*1,120,50,0,'Road','symbols/road.png',
                           [f'Price: 100','Serves as powerline']),
                    Button(mw,mh*2,120,50,1,'Highway','images/house_lv0.png')]
    app.buildingButtonActions = ['build_house','build_apartment','not_implemented']
    app.industryButtonActions = ['build_factory','build_office','not_implemented']
    app.utilitiesButtonActions = ['not_implemented','build_powerplant','not_implemented']
    app.municipalButtonActions = ['build_hospital','build_police','not_implemented',
                                  'not_implemented','not_implemented']
    app.roadButtonActions = ['build_road','not_implemented']
    app.mainButtonSub = [app.buildingBtns,app.industryBtns,
                         app.utilitiesBtns,app.municipalBtns,
                         app.roadBtns]
    app.buttonToggled = False
    app.numButtonToggled = 0

#checks which buttons are pressed and runs the action. 
def checkButtons(app,mouseX,mouseY):
    if app.buttonToggled and app.numButtonToggled:
        for button in app.mainButtonSub[app.numButtonToggled]:
            if button.isPressed(mouseX,mouseY):
                if app.numButtonToggled == 0:
                    button.action(app,app.buildingButtonActions[button.index]) 
                elif app.numButtonToggled == 1:
                    button.action(app,app.industryButtonActions[button.index])
                elif app.numButtonToggled == 2: 
                    button.action(app,app.utilitiesButtonActions[button.index])
                elif app.numButtonToggled == 3: 
                    button.action(app,app.municipalButtonActions[button.index])
                elif app.numButtonToggled == 4: 
                    button.action(app,app.roadButtonActions[button.index])
                return
    for button in app.mainButtons:
        if button.isPressed(mouseX,mouseY):
            app.buttonToggled = not app.buttonToggled
            app.numButtonToggled = button.index 

#-------------------------------------------------------------------------------
# Misc Functions

# Copied from CMUGraphicsPILDemo 
def openImage(fileName):
    return Image.open(os.path.join(pathlib.Path(__file__).parent,fileName))

#Returns maximum build potential based on proximity
def maxBuildPotential(app,row,col,buildingType):
    counter = 0
    if col != 0 and isinstance(app.board[row][col-1],Road):
        counter += 1 
    if col != app.boardCols and isinstance(app.board[row][col+1],Road):
        counter += 1
    if row != app.boardRows and isinstance(app.board[row+1][col],Road):
        counter += 1
    if row != 0 and isinstance(app.board[row-1][col],Road):
        counter += 1
    elevationPotential = 1 - (app.boardElevation[row][col] / 9)
    roadPotential = 0 
    if buildingType == House:
        roadPotential = 1 - abs(1 - counter)/3
    if buildingType == Apartment:
        roadPotential = 1 - abs(2 - counter)/2
    return (elevationPotential + roadPotential)/2 

