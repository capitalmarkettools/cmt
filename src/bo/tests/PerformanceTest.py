'''
Created on Jul 23, 2013

@author: Capital Market Tools
'''
import unittest

from src.models import Portfolio, ModelPosition
from src.bo.Date import Date
from src.bo.instruments.FinancialInstrument import CreatePosition
from src.bo.MarketDataContainer import MarketDataContainer

class PerformanceTest(unittest.TestCase):


    def setUp(self):
        self.marketId = 'TEST1'
        
    def testCalculatePerformanceTEST1Portfolio1Y(self):
        #load portfolio as of start and value
        #load portfolio as of end and value
        #sum up all ADD and REMOVE Transaction
        #% return = {end - start + SUM(ADD) - SUM(REMOVE)} / Start
        startPortfolio =Portfolio.objects.get(name='TEST1')
        start = Date(month=8,day=30,year=2011)
        startDjangoPositions = ModelPosition.objects.filter(portfolio=startPortfolio, asOf=start)
        for djangoPosition in startDjangoPositions:
            position = CreatePosition(djangoPosition)
            startPortfolio.addPosition(position)
        marketDataContainer = MarketDataContainer()
        for position in startPortfolio.positions:
            marketDataContainer.add(position.marketData(pricingDate=start, marketId=self.marketId))
        for position in startPortfolio.positions:
            position.marketDataContainer = marketDataContainer
        startValue = startPortfolio.NPV(pricingDate=start,marketId=self.marketId)
        print 'Start value = %f' % startValue
        
        endPortfolio =Portfolio.objects.get(name='TEST1')
        end = Date(month=9,day=12,year=2011)
        endDjangoPositions = ModelPosition.objects.filter(portfolio=endPortfolio, asOf=end)
        for djangoPosition in endDjangoPositions:
            position = CreatePosition(djangoPosition)
            endPortfolio.addPosition(position)
        marketDataContainer = MarketDataContainer()
        for position in endPortfolio.positions:
            marketDataContainer.add(position.marketData(pricingDate=end, marketId=self.marketId))
        for position in endPortfolio.positions:
            position.marketDataContainer = marketDataContainer
        endValue = endPortfolio.NPV(pricingDate=end,marketId=self.marketId)
        print 'End value = %f' % endValue
        
        #Should add the looping over transactions that are ADD and REDUCE
        
        print 'Annualized Performance is %f' % (((endValue - startValue) / startValue) * 365.0 / (end.ql() - start.ql()))
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()