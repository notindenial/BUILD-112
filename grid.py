from cmu_graphics import *
from math import floor

# draws grid based on an isometric view
def drawGrid(app,row,col,color):
    tileWidthHalf = app.tileWidth /2
    tileHeightHalf = app.tileHeight /2
    x = app.width//2 + (row - col) * tileWidthHalf + app.offsetX * app.scale 
    y = app.height//2 + (app.offsetY - app.boardTop) * app.scale + (row + col) * tileHeightHalf 
    if app.showAdvanced:
        for zone in app.zones:
            if (row,col) in zone.grids:
                color = zone.color
        for grid in app.powerGrids:
            if (row,col) in grid.roadGrids: 
                color = 'gold'
    color = 'blue' if (row,col) in app.toggledGrids else color
    drawPolygon(x, y, x + tileWidthHalf, y + tileHeightHalf,x, y + app.tileHeight, 
                x - tileWidthHalf, y + tileHeightHalf, fill = color)
    # drawLabel(str(app.boardElevation[row][col]//10), x, y + tileHeightHalf)
                
    
    # if app.board[row][col].isinstance(Water):
    #     drawPolygon(x, y, x + tileWidthHalf, y + tileHeightHalf,x, y + tileHeight, 
    #             x - tileWidthHalf, y + tileHeightHalf, fill = color)
    # drawLabel(str(row) + ',' + str(col), x, y + tileHeightHalf) 

# returns x and y coordinates of grid at specific index

# adds grid to set of toggled grids
def toggleGrid(app, mouseX,mouseY):
    app.toggledGrids.add(findGrid(app,mouseX,mouseY))

# finds grid row,col coordinates based on screen x,y coordinates
def findGrid(app,x,y):
    tileWidthHalf = app.tileWidth /2
    tileHeightHalf = app.tileHeight /2 
    row = (((x-(app.width//2)-(app.offsetX*app.scale)) / tileWidthHalf 
            + (y-app.height//2-(app.offsetY - app.boardTop) * app.scale) 
            / tileHeightHalf) /2) 
    col = (((y-app.height//2-(app.offsetY - app.boardTop) * app.scale) / tileHeightHalf 
            - (x-app.width//2-app.offsetX*app.scale) / tileWidthHalf) /2)
    row = floor(row)
    col = floor(col)
    # if row >= app.boardRows or col >= app.boardCols or row < 0 or col < 0:
    #     return None
    return (row,col)

# returns set of grids within a rectangular grid area
def getGridsSet(row,col,width,height):
    output = set()
    for x in range(row,row+width):
        for y in range(col,col+height):
            output.add((x,y))
    return output

def nearestGrid(app,row,col):
    if row < 0:
        row = 0
    elif row >= app.boardRows:
        row = app.boardRows
    if col < 0:
        col = 0
    elif col >= app.boardCols:
        col = app.boardCols 
    return (row,col)

def findGridCenter(app,row,col):
    x,y = calcCoords(app,row,col)
    return (x-app.tileHeightHalf,y)

# returns x,y screen coordinates based on grid row and col inputs
def calcCoords(app,row,col):
    x = app.width//2 + (row - col) * app.tileWidthHalf + app.offsetX * app.scale 
    y = app.height//2 + (app.offsetY - app.boardTop) * app.scale + (row + col) * app.tileHeightHalf 
    return x,y

def connectedPowerGrids(app,row,col):
    connectedGrids = []
    for powerGrid in app.powerGrids:
        for x,y in [(-1,0),(0,-1),(1,0),(0,1)]:
            if (row+x,col+y) in powerGrid.roadGrids:
                connectedGrids.append(powerGrid)
                break
    return connectedGrids 

