BUILD 112:
BUILD 112 is a city builder game emulating the progression and development of 
a city. Starting with limited resources, your goal is to slowly progress your 
city by building infrastructure that facilitates your economy. The goal of the 
player is to serve as the mayor, building infrastructure and zone areas to 
satisfy the citizen’s demands. 


How to run the project: 
- run the main.py file
- game is based on using your mouse to select grids and build on them. 
  click on a grid to select it. Then press h or r to build houses and roads.
  to build other features, just use the buttons on the side. All possible 
  features are documented here. 

Libraries Installed: 
 1. from cmu_graphics import *
    - CMU Graphics Package
 2. from math import floor
    - floor function to round numbers
 3. from noise import pnoise2,pnoise3
    - noise algorithm used to generate terrain elevation
 4. PIL import Image
 5. import os, pathlib
    - Image, os, pathlib used to interpret images in directory to be displayed
      using the CMU Graphics Package
 6. import random 
    - used for random terrain generation with the noise algorithm 
      and zoning(autobuilding) feature

Shortcut Commands: 
  1. Developer: 
        (On Menu) Press [s] to skip to game (or spam [space])
        (On Game) Press [1] for new game(regenerates map)
        (On Game) Press [2] for 10000 money

  2. Freeplay Commands: 
        Control
            press/hold [k/l] to zoom view
            press/hold [arrow keys] to pan view
            press [esc] to unselect grid(s)
            press [m] to return to menu 
        View
            press [e] to view elevation map
            press [v] to view zones and grids
        Build
            press [h] to build house
            press [r] to build road
        Delete
            press [d] to delete
            press [c] to clear zoning
        Gameplay
            press [n] for a new day
        
