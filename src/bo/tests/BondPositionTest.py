'''
Created on Oct 22, 2009

@author: capitalmarkettools
'''
import unittest
import QuantLib
from src.bo.instruments import BondPosition
from src.bo import MarketDataContainer, Date, ErrorHandling, Enum
from src.models import InterestRateCurve

class Test(unittest.TestCase):
    '''Unit test of BondPosition
    '''
    def setUp(self):
        self.pricingDate = Date.Date(month=9,day=12,year=2011)
        self.marketId = 'TEST1'
        QuantLib.Settings.instance().evaluationDate = self.pricingDate.ql()
        self.pos = BondPosition.BondPosition(amount=100, secId='TEST1')
    def testTickerName(self):
        self.failIf(self.pos.secId <> 'TEST1')
    def testAmount(self):
        self.failIf(self.pos.amount <> 100)
    def testNPV(self):
        marketDataContainer = MarketDataContainer.MarketDataContainer()
        marketData = self.pos.marketData(self.pricingDate, self.marketId)
        #print marketData
        marketDataContainer.add(marketData)
        self.pos.setMarketDataContainer(marketDataContainer)
        #print round(self.pos.NPV(self.pricingDate, self.marketId),2)
        self.failIf(round(self.pos.NPV(self.pricingDate, self.marketId),2) <> 10003.51)
    def test__str__(self):
        self.failIf(str(self.pos) <> '<<class \'src.bo.instruments.BondPosition.BondPosition\'>,TEST1,100>')
    def testExceptionMarketDataMissing(self):
        self.assertRaises(ErrorHandling.MarketDataMissing,
                          self.pos.NPV, Date.Date(1,1,2009))
    def testPriceToYield(self):
        marketDataContainer = MarketDataContainer.MarketDataContainer()
        marketData = self.pos.marketData(self.pricingDate, self.marketId)
        marketDataContainer.add(marketData)
        self.pos.setMarketDataContainer(marketDataContainer)
        #print round(self.pos.PriceToYield(80, self.pricingDate, self.marketId),5)
        #print round(self.pos.PriceToYield(90, self.pricingDate, self.marketId),5)
        #print round(self.pos.PriceToYield(100, self.pricingDate, self.marketId),5)
        self.failIf(round(self.pos.PriceToYield(80, self.pricingDate, self.marketId),5) <> 0.03582) 
        self.failIf(round(self.pos.PriceToYield(90, self.pricingDate, self.marketId),5) <> 0.02214) 
        self.failIf(round(self.pos.PriceToYield(100, self.pricingDate, self.marketId),5) <> 0.00995) 
    
    def testYieldToPrice(self):
        marketDataContainer = MarketDataContainer.MarketDataContainer()
        marketData = self.pos.marketData(self.pricingDate, self.marketId)
        marketDataContainer.add(marketData)
        self.pos.setMarketDataContainer(marketDataContainer)
        #print round(self.pos.YieldToPrice(0.01, self.pricingDate, self.marketId),5)
        #print round(self.pos.YieldToPrice(0.03, self.pricingDate, self.marketId),5)
        #print round(self.pos.YieldToPrice(0.05, self.pricingDate, self.marketId),5)
        #print round(self.pos.YieldToPrice(0.07, self.pricingDate, self.marketId),5)
        self.failIf(round(self.pos.YieldToPrice(0.01, self.pricingDate, self.marketId),5) <> 99.95698) 
        self.failIf(round(self.pos.YieldToPrice(0.03, self.pricingDate, self.marketId),5) <> 84.10743) 
        self.failIf(round(self.pos.YieldToPrice(0.05, self.pricingDate, self.marketId),5) <> 70.83034) 
        self.failIf(round(self.pos.YieldToPrice(0.07, self.pricingDate, self.marketId),5) <> 59.70515) 

    def testPriceWith2Curves(self):
        marketDataContainer = MarketDataContainer.MarketDataContainer()
        marketData = self.pos.marketData(self.pricingDate, self.marketId)
#        print marketData[0].buildZeroCurve().nodes()
        marketDataContainer.add(marketData)
        self.pos.setMarketDataContainer(marketDataContainer)
        price1 = round(self.pos.NPV(self.pricingDate, self.marketId),5)
        marketData[0].shift(0.01)
#        print marketData[0].buildZeroCurve().nodes()
        marketDataContainer1 = MarketDataContainer.MarketDataContainer()
        marketDataContainer1.add(marketData)
        self.pos.setMarketDataContainer(marketDataContainer1)
        #add dirty flag to position to run setupql again. add add marketdatacontainer method
        price2 = round(self.pos.NPV(self.pricingDate, self.marketId),5)
        self.failIf(price1 == price2)
        
    def testLoadAndSaveMarketData_TODO(self):
        #curve should never exist
        self.pos.loadAndSaveMarketData(pricingDate=Date.Date(1,1,2009), 
                                       marketId=self.marketId)
        #now, curve should exist
        irCurve = InterestRateCurve()
        irCurve.ccy = Enum.Currency('USD')
        irCurve.index = Enum.Index('LIBOR')
        irCurve.term = 'M'
        irCurve.numTerms = 3
        irCurve.pricingDate = Date.Date(1,1,2009)
        irCurve.marketId = self.marketId
        irCurve.load()
        #now, delete again so that next test will work
        irCurve.delete()
        
def suite():
    return unittest.makeSuite(Test)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testTickerName']
    unittest.main()