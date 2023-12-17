from cmu_graphics import *
from grid import *
from constructables import *
from player import * 
from math import floor
from noise import pnoise2,pnoise3
from PIL import Image
import os, pathlib, random

# Change log:
# Add Terrain Generation (Done)
# Finish Road T and R toggle (Done)
# Add electric grids (Done)
# Added Popularity and Gameover
# UI Improvements
# Reorganize Code

# Version TP2
# Fix game buttons and building draw from buttons (Done)
# Fix road draw (Done)
# Add Utilities (Done)
# Add Municipal (Done)
# Rework game elements (price restrictions) (Done)
# Smooth zoning feature (Done)
# Implement menu screen functionality (Done)

#-------------------------------------------------------------------------------
# Initialization 
 
def onAppStart(app):
    app.width = 1200
    app.height = 1000
    app.center = (app.width/2, app.height/2)
    app.noise = pnoise3
    newGame(app)

def newGame(app):
    app.gameOver = False
    app.toggledGrids = {(0,0)}
    app.gridSelected = (0,0)
    app.gridMouseReleased = (0,0)
    app.zones = [] 
    app.factories = []
    app.powerGrids = []
    app.waterGrids = set()
    app.isGridSelected = False
    app.isToggling= False
    app.isZoning = False
    app.showAdvanced = False
    app.drawNewDay = True
    app.drawCommands = True
    app.notEnoughMoney = False
    app.notImplementedYet = False
    app.isMultiToggling = False
    app.invalidBuildAttempt = False
    app.drawElevation = True
    app.drawButtonDescription = False
    app.hoveredButton = None
    loadScaling(app)
    loadGrid(app,20,20)
    loadButtons(app)
    loadNewGame(app)
    loadImages(app)
    loadText(app)

#-------------------------------------------------------------------------------
#Splash Screen

def welcome_redrawAll(app):
    drawIntro(app)

def welcome_onMousePress(app,mouseX,mouseY):
    setActiveScreen('start')

def welcome_onKeyPress(app,key):
    if key == 'space':
        setActiveScreen('description')
    if key == 's':
        setActiveScreen('game')

def welcome_onMousePress(app,mouseX,mouseY):
    setActiveScreen('description')

#-------------------------------------------------------------------------------
# Game Description Displayed
def description_redrawAll(app):
    drawDescription(app)

def description_onMousePress(app,mouseX,mouseY):
    setActiveScreen('menu')

def description_onKeyPress(app,key):
    if key == 'space':
        setActiveScreen('menu')
#-------------------------------------------------------------------------------
# Menu Displayed
def menu_redrawAll(app):
    drawMenu(app)
    menuDrawButtons(app)

def menu_onMousePress(app,mouseX,mouseY): 
     for button in app.menuButtons:
        if button.isPressed(mouseX,mouseY):
            if button.index == 0:       
                setActiveScreen('game')
            elif button.index == 1:       
                setActiveScreen('game')
                newGame(app) 
                if app.noise == pnoise3:
                    app.noise == pnoise2
                else:
                    app.noise == pnoise3
            elif button.index == 2:
                setActiveScreen('description')
            elif button.index == 3:
                setActiveScreen('credits')

def menu_onKeyPress(app,key):
    if key == 'space':
        setActiveScreen('game')

#-------------------------------------------------------------------------------
#Game Credits... 

def credits_redrawAll(app):
    drawCredits(app)

def credits_onKeyPress(app,key):
    if key == 'space':
        setActiveScreen('menu')

def credits_onMousePress(app,mouseX,mouseY):
    setActiveScreen('menu')


#-------------------------------------------------------------------------------
#Game Settings... 

# def setting_redrawAll(app):
#     draw

#-------------------------------------------------------------------------------
#Game Running...

def game_redrawAll(app):
    drawBoard(app)
    gameDrawButtons(app)
    if app.drawCommands:
        drawCommands(app)
    drawPlayerStats(app)
    if app.gameOver:
        drawGameOver(app)
        return
    if app.drawNewDay: 
        drawNewDay(app)
        return
    if app.drawButtonDescription:
        drawButtonDescription(app)
    drawErrorMessages(app)

# Hotkeys 
def game_onKeyPress(app,key):
    if app.gameOver:
        if key == 'space':
            resetMessages(app)
            newGame(app)
        return
    if app.drawNewDay:
        if key == 'space':
            resetMessages(app)
            app.drawNewDay = False
        return
    panKeyCheck(app,key)
    zoomKeyCheck(app,key)
    if key == 'escape':
        app.isGridSelected = False
    # View Key Toggling 
    elif key == 't':
        app.drawCommands = not app.drawCommands
    elif key == 'e':
        app.drawElevation = not app.drawElevation
    elif key == 'v':
        app.showAdvanced = not app.showAdvanced
    elif key == 'm':
        setActiveScreen('menu')
    # Build Keys
    elif key == 'h':
        row,col = app.gridSelected
        elevationCost = 0
        elevation = app.boardElevation[row][col]
        if elevation <= 0:
            app.invalidBuildAttempt = True
            return
        elif elevation >= 5:
            elevationCost = 200
        if app.isGridSelected:
            if app.board[row][col] == None:
                if app.player.money >= House().cost:
                    app.board[row][col] = House()
                    app.player.population += app.board[row][col].population
                    app.player.money -= app.board[row][col].cost
                    for grid in app.powerGrids:
                        grid.updateHouses(app)
                else:
                    app.notEnoughMoney = True
    elif key == 'r':
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
    # Delete Keys
    elif key == 'd':
        if app.isGridSelected: 
            row,col = app.gridSelected
            if isinstance(app.board[row][col],Residential):
                app.player.population -= app.board[row][col].population  
            if app.board[row][col] != None:
                app.player.money += app.board[row][col].cost/4//1000
            app.board[row][col] = None
    elif key == 'c':
        app.zones = []
    # Gameplay Keys 
    elif key == 'n':
        app.player.newDay(app)
        if app.player.happiness == 0:
            app.gameOver = True
        app.drawNewDay = True
    #Feature Demonstration: 
    elif key == '1':
        newGame(app)
    elif key == '2':
        app.player.money += 10000

# grid highlighting when hovering
def game_onMouseMove(app,mouseX,mouseY):
    if app.drawNewDay or app.gameOver:
        return 
    if not app.isGridSelected:
        app.toggledGrids = set()
        toggleGrid(app,mouseX,mouseY)
    if app.buttonToggled:
        for button in app.mainButtonSub[app.numButtonToggled]:
            if button.isPressed(mouseX,mouseY):
                app.drawButtonDescription = True
                app.hoveredButton = button
                app.mouseX,app.mouseY = mouseX,mouseY
                return
    # for button in app.mainButtons:
    #     if button.isPressed(mouseX,mouseY):
    #         app.drawButtonDescription = True
    #         app.hoveredButton = button
    #         app.mouseX,app.mouseY = mouseX,mouseY
    #         return 
    app.drawButtonDescription = False
        
    
# multi-grid toggling 
def game_onMouseDrag(app,mouseX,mouseY):
    if app.drawNewDay:
        return
    nRow,nCol = findGrid(app,mouseX,mouseY)
    nRow,nCol = nearestGrid(app,nRow,nCol)
    oRow,oCol = app.gridSelected 
    app.toggledGrids = set()
    for i in range(min(nRow,oRow)+1,max(nRow,oRow)+2):
        for j in range(min(nCol,oCol),max(nCol,oCol)+1):
            x,y = findGridCenter(app,i,j)
            toggleGrid(app,x,y)
    if len(app.toggledGrids) >= 2:
        app.isMultiToggling = True


# stop multi-grid toggling
def game_onMouseRelease(app,mouseX,mouseY):
    if app.isGridSelected and app.isMultiToggling:
        row,col = findGrid(app,mouseX,mouseY)
        row,col = nearestGrid(app,row,col)
        app.gridMouseReleased = (row,col)
    app.isMultiToggling = False

# button and grid recognition and selection 
def game_onMousePress(app,mouseX,mouseY):
    resetMessages(app)
    currGrid = findGrid(app,mouseX,mouseY)
    row,col = currGrid
    pRow, pCol = app.gridSelected
    grid = app.board[pRow][pCol]
    # if isinstance(grid,Road):
    #     print(connectedRoads(app,row,col,set()))
    if app.isGridSelected and isinstance(grid,Building):
        for button in grid.buttons:
            if button.isPressed(mouseX,mouseY):
                button.action(app,grid.buttonActions[button.index])
    if app.buttonToggled and app.numButtonToggled < 5:
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
            if button.index == 5:             
                setActiveScreen('menu')
                return
            app.buttonToggled = not app.buttonToggled
            app.numButtonToggled = button.index 
            return
    
    if (app.gridSelected != currGrid and row >= 0 and row < app.boardRows 
        and col >= 0 and col < app.boardCols): 
        app.gridSelected = currGrid
        app.toggledGrids = set()
        toggleGrid(app, mouseX,mouseY)
        app.isGridSelected = True
    else: 
        app.toggledGrids = set()
        app.isGridSelected = False
        app.showZones = False

# check key holds for pan/zooming 
def game_onKeyHold(app,keys):
    app.timeHeld += 1
    app.panSpeed = floor(2 ** (0.005 * app.timeHeld))
    app.zoomSpeed = floor(2 ** (0.005 * app.timeHeld))
    for key in keys:
        panKeyCheck(app,key)
        zoomKeyCheck(app,key)

# reset variables for pan/zooming 
def game_onKeyRelease(app,key):
    app.timeHeld = 0
    app.panSpeed = 1
    app.zoomSpeed = 1

#-------------------------------------------------------------------------------
#draw functions for each section

# Welcome Layout
def drawIntro(app):
    cW,cH = app.center
    drawImage(CMUImage(app.logo),cW,cH-170,width=250,height=250,align='center')
    drawLabel('BUILD 112',cW,cH,align='center',size=80,
              bold=True, fill='black',font='arial')
    drawLabel('press space or click to begin your journey',cW,cH+60,
              align='center',size=20,fill='black',font='monospace')

# Description Layout
def drawDescription(app):
    cW,cH = app.center
    drawImage(CMUImage(app.city),cW,cH,align='center')
    drawLabel('BUILD 112',cW,cH-210,align='center',size=30,
              border='white',fill='white',font='orbitron')
    drawRect(cW,cH-210,160,50,align='center',fill=None,border='white')
    drawRect(cW,cH-180,380,300,align='top',fill='white',border='gold')
    for i in range(len(app.menuText)):
        y = cH - 150 + 20*i 
        drawLabel(app.menuText[i],cW-180,y,align='left',size=16,
                  fill='black',font='orbitron')
    drawLabel('press space to continue',cW,cH+110,fill='black',font='orbitron')

# Menu Layout
def drawMenu(app):
    cW,cH = app.center
    drawImage(CMUImage(app.city),cW,cH,align='center')
    drawLabel('BUILD 112',cW,cH-210,align='center',size=30,
              border='white',fill='white',font='orbitron')
    drawRect(cW,cH-210,160,50,align='center',fill=None,border='white')
    
# Menu buttons
def menuDrawButtons(app):
    for menuButton in app.menuButtons:
        menuButton.draw()

# Credit Screen
def drawCredits(app):
    cW,cH = app.center 
    drawImage(CMUImage(app.city),cW,cH,align='center')
    drawLabel('BUILD 112',cW,cH-210,align='center',size=30,
              border='white',fill='white',font='orbitron')
    drawRect(cW,cH-210,160,50,align='center',fill=None,border='white')
    drawRect(cW,cH-180,350,300,align='top',fill='white',border='gold')
    for i in range(len(app.creditsText)):
        y = cH - 150 + 20*i 
        drawLabel(app.creditsText[i],cW-170,y,align='left',size=16,
                  fill='black',font='orbitron')
    # drawLabel(,cW,cH-160,fill='black',font='orbitron')
    drawLabel('press space to return',cW,cH+110,fill='black',font='orbitron')

# Game buttons
def gameDrawButtons(app):
    for mainButton in app.mainButtons:
        mainButton.draw()
    if app.buttonToggled:
        if app.numButtonToggled == 5:
            return
        for button in app.mainButtonSub[app.numButtonToggled]:
            button.draw()

# Game board
def drawBoard(app):
    for row in range(app.boardRows):
        for col in range(app.boardCols):
            if app.drawElevation:
                drawElevationBoard(app,row,col)
            else:
                drawStandardBoard(app,row,col)
    for row in range(app.boardRows):
        for col in range(app.boardCols):
            if isinstance(app.board[row][col],Road):
                app.board[row][col].updateConnections(app,row,col)
            if isinstance(app.board[row][col],Building):
                app.board[row][col].draw(app,row,col)
                if app.gridSelected == (row,col):
                    app.board[row][col].drawButtons()
#draw gradients
def drawElevationBoard(app,row,col):
    elevation = app.boardElevation[row][col]
    if elevation <= 0:
        shift = elevation/4 if elevation > -4 else -1
        drawGrid(app,row,col,rgb(1,235+shift*80,250+shift*20))
    elif elevation <= 1:
        drawGrid(app,row,col,rgb(82, 199, 85))
    else:
        shift = elevation/9 if elevation < 9 else 1
        drawGrid(app,row,col,rgb(82-shift*77,199-shift*97,85-shift*77))

#draw with only 3 colors 
def drawStandardBoard(app,row,col):
    elevation = app.boardElevation[row][col]
    if elevation <= 0:
        drawGrid(app,row,col,rgb(0, 206, 241))
    elif elevation <= 5:
        drawGrid(app,row,col,rgb(67, 180, 70))
    else: 
        drawGrid(app,row,col,'green')

# Hotkey Commands        
def drawCommands(app):
    drawRect(app.width*5/6,app.height-10,300,len(app.commandText)*18+15,
             align='bottom',fill='white',border='gold')
    for i in range(len(app.commandText)):
        y = app.height - 18*i - 22 
        drawLabel(app.commandText[i],app.width*5/6,y,align='bottom',size=16,
                  fill='Navy',font='arial')

# Game stats bar
def drawPlayerStats(app): 
    drawRect(0,0,app.width,50,fill='lightSkyBlue')
    drawLabel(f'Money: {app.player.money}',120,25,fill='white',size=20,)
    drawLabel(f'Population: {app.player.population}',270,25,fill='white',size=20)
    drawLabel(f'Day: {app.player.day}',400,25,fill='white',size=20)
    drawImage(CMUImage(openImage('old_images/logo.jpg')),0,0,width=49,height=49)
    drawLabel(f'Happiness: {app.player.happiness}',850,25,fill='white',size=20)

    drawLine(0,50,app.width,50,fill='gold')
    cW,cH = app.center
    drawPolygon(cW-150,0,cW-130,80,
                cW+130,80,cW+150,0,
                fill='white',border='gold')
    drawLabel('BUILD 112',cW,40,align='center',size=45,
              border='navy',fill='navy',font='orbitron')
    
# New Day Cycle Display
def drawNewDay(app):
    cW,cH = app.center
    drawRect(cW,cH,300,600,fill='lightSkyBlue',border='gold',borderWidth=5,
             align='center')
    drawRect(cW,cH-260,160,50,align='center',fill=None,border='white')
    drawLabel(f'Day {app.player.day}',cW,cH-260,align='center',size=30,
              border='white',fill='white',font='orbitron')
    if app.player.day == 0:
        drawLabel(f'Population: {app.player.population}',cW-130,cH-200,
                  align='left',fill='white',size = 20)
        drawLabel(f'Money: {app.player.money}',cW-130,cH-150,
                  align='left',fill='white',size = 20)
    else:
         drawLabel(f'Population: {app.player.population}',cW-130,cH-200,
                   align='left',fill='white',size = 20)
         drawLabel(f'Population Added: {app.player.population-app.player.prevPop}',
                   cW-130,cH-150,align='left',fill='white',size = 20)
         drawLabel(f'Money: {app.player.money}',cW-130,cH-100,
                   align='left',fill='white',size = 20)
         drawLabel(f'Collected Taxes: {app.player.taxedIncome}',cW-130,cH-50,
                   align='left',fill='white',size = 20)
         drawLabel(f'Industry Earnings: {app.player.industryIncome}',cW-130,cH,
                   align='left',fill='white',size = 20)
         drawLabel(f'Happiness: {app.player.happiness}',cW-130,cH+50,
                   align='left',fill='white',size = 20)
    drawLabel('press [space] or click to continue',cW,cH+275,
              align='center',fill='white',size = 15)

def drawGameOver(app):
    cW,cH = app.center
    drawRect(cW,cH,300,600,fill='lightSkyBlue',border='gold',borderWidth=5,
             align='center')
    drawRect(cW,cH-260,160,50,align='center',fill=None,border='white')
    drawLabel(f'Day {app.player.day}',cW,cH-260,align='center',size=30,
              border='white',fill='white',font='orbitron')
    drawLabel(f'GAME OVER',cW,cH-20,align='center',size=30,
              border='white',fill='white',font='orbitron')
    drawLabel(f'Your failed your citizens',cW,cH+50,
            align='center',fill='white',size = 20)
    drawLabel('press [space] to restart',cW,cH+275,
              align='center',fill='white',size = 15)

# Error Messages Display
def drawErrorMessages(app):
    if app.notImplementedYet:
        drawLabel('Feature not implemented yet',app.width/2,app.height/2,size=20)
    if app.notEnoughMoney:
        cW,cH = app.center
        drawRect(cW,cH+10,230,45,fill='white',opacity=50,align='center')
        drawLabel('Not enough money!',cW,cH,size=20)
        drawLabel('Press [n] for a new day',cW,cH+20,size=20)
    if app.invalidBuildAttempt:
        drawLabel('Can\'t Build Here',app.width/2,app.height/2,size=20)

def drawButtonDescription(app): 
    button = app.hoveredButton
    drawRect(button.x+button.width+10,button.y,button.width,button.height,border='gold',
             fill='white')
    if isinstance(button.description,str):
        drawLabel(button.description,button.x+button.width+15,
                  button.y+button.height/2,align='left')
    else:
        l = len(button.description)
        for i in range(l):
            drawLabel(button.description[i],button.x+button.width+15,
                  button.y+button.height*(i+1)/(l+1),align='left')

# Tree Image Drawing
def drawTree(app,row,col):
    x,y = findGridCenter(app,row,col)
    drawImage(CMUImage(app.tree),x,y,width=app.tileHeight,height=app.tileHeight)

#-------------------------------------------------------------------------------
# load app variables 

def loadNewGame(app):
    app.player = Player(100)
    app.board = [([None] * app.boardRows) for row in range(app.boardCols)]
    random.seed()
    octaves = random.random()
    freq = 16.0 * octaves
    app.boardElevation = [([1] * app.boardRows) for row in range(app.boardCols)]
    for x in range(app.boardRows):
        for y in range(app.boardCols):
            n = float(app.noise(y/freq, x / freq, 1)*10+3)
            if n <= 0:
                app.waterGrids.add((x,y)) 
            app.boardElevation[x][y] = n
# Generated using the perlin noise algorithm referencing the following sites:
# https://pvigier.github.io/2018/10/08/terrain-generation-simulopolis.html 
# https://gamedev.stackexchange.com/questions/29044/how-can-i-generate-random-lakes-and-rivers-in-my-game 

def loadGrid(app,x,y):
    app.boardTop = 250
    app.boardRows = x
    app.boardCols = y 
    app.tileWidth = 1200/app.boardCols 
    app.tileHeight = app.tileWidth /2
    app.tileWidthHalf = app.tileWidth /2
    app.tileHeightHalf = app.tileHeight /2

def loadImages(app):
    app.logo = openImage('images/logo.png')
    app.city = openImage('images/city.jpg')
    app.tree = openImage('images/tree.png')

def loadText(app):
    app.menuText = ['As the mayor of a new town, your job is to grow the',
                    'city while managing the limited resources available.',
                    'Get creative and build a bustling city of the future!',
                    '(...or as close to one as this 35hr project gets you)']
    app.commandText = ['press [esc] to unselect grid(s)',
                       'press [e] to view elevation map',
                       'press [v] to view zones and grids',
                       'press [h] to build house',
                       'press [r] to build road',
                       'press [d] to delete',
                       'press [c] to clear zoning',
                       'press [n] for a new day',
                       'press [m] to return to menu']
    app.creditsText = ['Game made for 112',
                       'Code and layout written by Daniel Lin',
                       'Project Documentation: https://bit.ly/BUILD112',
                       'Implementations:',
                       '1. Isometric Grid Layout + Zoom/Panning',
                       '2. Randomized Perlin Noise Elevation Mapping',
                       '3. Zoning Based Autobuilding',
                       '4. Recursive Electric Grid Mapping',
                       '5. 7 Different Building Elements']
    
def loadScaling(app):
    app.scale = 1.0000 
    app.offsetX = 0
    app.offsetY = 0
    app.timeHeld = 0
    app.panSpeed = 1
    app.zoomSpeed = 1

def resetMessages(app):
    app.notEnoughMoney = False
    app.notImplementedYet = False
    app.drawNewDay = False 
    app.invalidBuildAttempt = False

#-------------------------------------------------------------------------------
# change offset and scaling parameters based on key inputs

def panKeyCheck(app,key):
    if key == 'up' and app.offsetY < (app.width/2 - 200):
        app.offsetY += 10 * (1/app.scale) * app.panSpeed
    elif key == 'down' and app.offsetY > -(app.width/2 - 200):
        app.offsetY -= 10 * (1/app.scale) * app.panSpeed
    elif key == 'right' and app.offsetX < (app.height/2 - 250):
        app.offsetX += 10 * (1/app.scale) * app.panSpeed
    elif key == 'left' and app.offsetX > -(app.height/2 - 250):
        app.offsetX -= 10 * (1/app.scale) * app.panSpeed

def zoomKeyCheck(app,key):
    if key == 'k' and app.scale < 2:
        app.scale += 0.1 * app.zoomSpeed
    elif key == 'l' and app.scale >= 0.2:
        app.scale -= 0.1 * app.zoomSpeed
    app.tileWidth = (app.width/app.boardCols)  * app.scale
    app.tileHeight = (app.width/app.boardCols/2)  * app.scale
    app.tileWidthHalf = app.tileWidth /2
    app.tileHeightHalf = app.tileHeight /2

#-------------------------------------------------------------------------------
# Copied from CMUGraphicsPILDemo 
def openImage(fileName):
    return Image.open(os.path.join(pathlib.Path(__file__).parent,fileName))

#-------------------------------------------------------------------------------
# main 
# runAppWithScreens referenced from the F23_demos.zip found of the 15-112 piazza
# post under note @2231

def main():
    runAppWithScreens(initialScreen='welcome')

main()
