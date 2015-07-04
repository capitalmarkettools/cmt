'''
Created on Jul 8, 2011
@author: Capital Market Tools
'''
import unittest, copy
from src.bo import MarketDataScenario, Date
from src.models import StockPrice, Equity, InterestRateCurve

class MarketDataScenarioTest(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def testSingleStockPriceScenario(self):
        stockPriceA = StockPrice()
        equity = Equity()
        equity.ticker = 'TEST1'
        stockPriceA.equity = equity
        stockPriceA.pricingDate = Date.Date(month=9,day=12,year=2011)
        stockPriceA.mid = 100.0
        scenarioBase = MarketDataScenario.MarketDataScenario()
        scenarioBase.name = 'Base'
        scenarioBase.marketData = stockPriceA
        #print "Base:" + str(scenarioBase)
        scenarioUp = MarketDataScenario.MarketDataScenario()
        scenarioUp.name = 'Up'
        stockPriceB = copy.copy(stockPriceA)
        stockPriceB.mid = stockPriceB.mid * 1.01
        scenarioUp.marketData = stockPriceB
        #print "Base:" + str(scenarioBase)
        #print "Up:" + str(scenarioUp)
         
    def testSingleIRCurveScenario(self):
        irA = InterestRateCurve()
        irA.ccy = "USD"
        irA.index = "LIBOR"
        irA.term = 'M'
        irA.numTerms = 3
        irA.marketId = 'TEST1'
        irA.pricingDate = Date.Date(month=9, day=12, year=2011)
        irA.load()
        scenarioBase = MarketDataScenario.MarketDataScenario()
        scenarioBase.name = 'Base'
        scenarioBase.marketData = irA
        #print scenarioBase
        scenarioUp = MarketDataScenario.MarketDataScenario()
        scenarioUp.name = 'Up'
        irB = copy.copy(irA)
        for item in irB.rates:
            item.mid = item.mid * 1.01
        scenarioUp.marketData = irB
        #print scenarioBase
        #print scenarioUp
    
def suite():
    return unittest.makeSuite(MarketDataScenarioTest)
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()