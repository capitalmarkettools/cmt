'''
Created on Oct 26, 2009

@author: capitalmarkettools
'''
import QuantLib
import scipy.stats
from src.models import Portfolio
from src.bo import VARUtilities, cmt
from src.bo.Enum import TimePeriod
from src.bo.static import Calendar
from src.bo.Date import Date
from src.bo.MarketDataContainer import MarketDataContainer
from src.bo.decorators import log
from src.bo.ErrorHandling import OtherException
from src.bo.instruments.BondPosition import BondPosition
from src.bo.instruments.EquityPosition import EquityPosition

class HVARTimeStepData(cmt.cmt):
    def __init__(self , date=None):
        #date of time step
        self.date = date
        #market data on time step. We assume that the sequence of market data item does not change
        #after it has been established once
        self.marketDataContainer = MarketDataContainer()
        #shifts between previous time step and this time step for each market data element
        self.shifts = []
        #scenarios with name equal to the date
        self.scenarios = [] 
        #market data representing shifted market data for each time step
        #list represents: [None, pricingDate mkt data shifted by shift(d(0),d(1)) ...
        self.scenarioMarketDataContainer = MarketDataContainer()
        #value of portfolio on date
        self.value = None
        self.pnl = None
        #percent return
        self.percentReturn = None

#    def __str__(self):
#        r = ''
#        r += 'marketDataContainer: ' + str(self.marketDataContainer)
class HistoricalVAR(cmt.cmt):
    '''
    Analysis to calculate Historical VAR
    '''
    def __init__(self, pricingDate = None, portfolio = None, timeSteps = None,
                 confidenceInterval = None, marketId = ''):
        '''
        Input: pricingDate, portfolio, timeSteps
        timeSteps is HVARTimeStepData object and defines start, end, and all dates
        '''
        if timeSteps == None:
            raise OtherException('timeSteps cannot be none')
        self.pricingDate = pricingDate
        self.start = timeSteps.start
        self.end = timeSteps.end
        self.timeStepDataList = []
        for item in timeSteps.timeSteps:
            self.timeStepDataList.append(HVARTimeStepData(date = item))
        self.portfolio = portfolio
        self.marketId = marketId
        self.todaysMarketDataContainer = MarketDataContainer()
        self.confidenceInterval = confidenceInterval
        self.upToDate = False
        self.pnls = []
        self.returns = []
        
    @log
    def generateTodaysMarketDataContainer(self):
        ''' 
        Generate today's market data for portfolio 
        '''
        for position in self.portfolio.positions:
            self.todaysMarketDataContainer.add(position.marketData(self.pricingDate, self.marketId))

    @log
    def generateAllHistoricalMarketDataContainers(self):
        '''
        Generates all market data containers for each time step
        '''
        for timeStep in self.timeStepDataList:
            for position in self.portfolio.positions:
                timeStep.marketDataContainer.add(position.marketData(timeStep.date, self.marketId))
                #scenario market data is based on as of market data. Shift is applied later
                timeStep.scenarioMarketDataContainer.add(position.marketData(self.pricingDate, self.marketId))
#        print '****Debug output HVAR*****'
#        for timeStep in self.timeStepDataList:
#            for m, s in zip(timeStep.marketDataContainer.marketDataList,
#                            timeStep.scenarioMarketDataContainer.marketDataList):
#                print m
#                print s
#        print '****Debug output HVAR done*****'

    @log
    def generateAllMarketDataShifts(self):
        first = True
        for timeStep in self.timeStepDataList:
            if first:
                prevTimeStep = timeStep
                first = False
                continue
            else:
                for marketData, prevMarketData in zip(timeStep.marketDataContainer.marketDataList,
                                                      prevTimeStep.marketDataContainer.marketDataList):
                    timeStep.shifts.append(marketData.createShiftCurve(prevMarketData))
                prevTimeStep = timeStep
                
    @log 
    def generateAllScenarios(self):
        first = True
        for timeStep in self.timeStepDataList:
            if first:
                first = False
                continue
            else:
                for marketData, shift in zip(timeStep.scenarioMarketDataContainer.marketDataList, 
                                             timeStep.shifts):
                    marketData.adjustWithShiftCurve(shift)
    
    @log
    def generateBaseValues(self):
        for position in self.portfolio.positions:
            position.setMarketDataContainer(self.todaysMarketDataContainer)
        value = self.portfolio.NPV(self.pricingDate, self.marketId)
        for timeStep in self.timeStepDataList:
            timeStep.value = value

    @log
    def generatePnls(self):
        first = True
        for timeStep in self.timeStepDataList:
            for position in self.portfolio.positions:
                position.setMarketDataContainer(timeStep.scenarioMarketDataContainer)
            value = self.portfolio.NPV(self.pricingDate, self.marketId)
            if first:
                timeStep.pnl = None
                first = False
            else:
                timeStep.pnl = value - timeStep.value
        
    @log
    def generateReturns(self):
        first = True
        for timeStep in self.timeStepDataList:
            if first:
                timeStep.percentReturn = None
                first = False
            else:
                timeStep.percentReturn = timeStep.pnl / timeStep.value

    @log
    def generateReturnsAndPnlsForStats(self):
        first = True
        for timeStep in self.timeStepDataList:
            if first:
                first = False
            else:
                self.pnls.append(timeStep.pnl)
                self.returns.append(timeStep.percentReturn)
                
    @log    
    def doAnalysis(self):
        '''
        Run historical VaR analysis. Can be re-run any time
        '''
#the following algorithm should be implemented:
#load today's position and today's market data
#generate shifts of market data for all time periods
#generate scenarios with shifts and today's market data
#run scenario analysis with simultaneous shifts
#output of scenario analysis is pnl vector
        self.generateTodaysMarketDataContainer()
        
        self.generateAllHistoricalMarketDataContainers()
        
        self.generateBaseValues()
        
        self.generateAllMarketDataShifts()

        self.generateAllScenarios()
     
        self.generatePnls()
        
        self.generateReturns()

        self.generateReturnsAndPnlsForStats()
        
        self.upToDate = True

    @log
    def getPnLList(self):
        '''
        Returns list of pnl values. Becuase pnl on first timestep is None
        we do not return it
        '''
        if self.upToDate == False:
            self.doAnalysis()
        return self.pnls
    @log
    def getDateList(self):
        '''
        Returns list of dates from timeSteps. This list includes the 
        first date. So, thi slist is one item longer than pnls and returns
        '''
        return [timeStep.date for timeStep in self.timeStepDataList]

    @log
    def getPercentile(self):
        '''
        Returns list of pnl values. Becuase pnl on first timestep is None
        we do not return it
        '''
        if self.upToDate == False:
            self.doAnalysis()
        return scipy.stats.scoreatpercentile(self.returns,100.0*(1-self.confidenceInterval))        
    @log
    def getMean(self):
        if self.upToDate == False:
            self.doAnalysis()
        return scipy.stats.nanmean(self.returns)
    @log
    def getStdDev(self):
        if self.upToDate == False:
            self.doAnalysis()
        return scipy.stats.moment(self.returns, 2)
    @log
    def run(self):
        return self.getPercentile()
               
def main():
    print 'Start'
    pricingDate = Date(month=9, day=12, year=2011)
    portfolio =Portfolio()
    QuantLib.Settings.instance().evaluationDate = pricingDate.ql()
    pos1 = BondPosition(100, 'TEST1')
    pos2 = EquityPosition(100,'TEST1')
    portfolio.addPosition(pos1)
    portfolio.addPosition(pos2)
    timePeriods = VARUtilities.VARTimePeriodsAndSteps()
    timePeriods.generate(start=Date(month=8,day=30,year=2011), 
                         end=Date(month=9,day=12,year=2011), num=1, 
                         term=TimePeriod('D').ql(), 
                         calendar=Calendar.US())
    #print 'timePeriods: ' + str(timePeriods)
    analysis = HistoricalVAR(pricingDate=pricingDate, portfolio=portfolio, timeSteps=timePeriods, 
                               confidenceInterval=0.95, marketId='TEST1')

    print 'HVaR = %f' % analysis.run()
    print 'End'
if __name__ == "__main__":
    main()