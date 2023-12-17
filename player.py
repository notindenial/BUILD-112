from constructables import Residential

class Player:
    def __init__(self,happiness,population=0,money=5000):
        self.population = population
        self.prevPop = 0
        self.money = money
        self.happiness = happiness
        self.happinessChange = 0
        self.taxRate = 10
        self.taxedIncome = 0
        self.industryIncome = 0
        self.day = 0

    def newDay(self,app):
        self.day += 1
        self.happiness = boardHappiness(app)
        self.taxedIncome = self.taxRate * self.population
        self.money += self.taxRate * self.population
        self.prevPop = self.population
        for zone in app.zones:
            zone.grow()
        for factory in app.factories: 
            self.industryIncome = (factory.incomePerPopulation * self.population
                                   - factory.managementCost)
            self.money += self.industryIncome

# Future Implementation 
def boardHappiness(app):
    totalHappiness = 0
    houseCount = 0
    for row in range(app.boardRows):
        for col in range(app.boardCols):
            currGrid = app.board[row][col]
            if isinstance(currGrid,Residential):
                houseCount += 1
                totalHappiness += currGrid.findHappiness(app,row,col)
    return totalHappiness//houseCount if houseCount != 0 else 100