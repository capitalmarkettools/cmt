'''
Created on Oct 22, 2009

@author: capitalmarkettools
'''
import unittest
from src.bo.instruments.EquityPosition import EquityPosition
from src.bo import MarketDataContainer, Date, ErrorHandling
from src.models import StockPrice

class TestEquityPosition(unittest.TestCase):
    """Unit test of EquityPosition"""
    def setUp(self):
        self._marketId = 'TEST1'
        self._pos = EquityPosition(100, 'TEST1')
        self._posMarketDataMissing = EquityPosition(100, 'GOOG')
#        self._marketDataMissingDate = Date.Date(month=1,day=3,year=2011)
        self._marketDataMissingDate = Date.Date(month=1,day=2,year=2009)
    def testTickerName(self):
        self.failIf(self._pos.secId <> self._marketId)
    def testAmount(self):
        self.failIf(self._pos.amount <> 100)
    def testNPV(self):
        pricingDate = Date.Date(day=12,month=9,year=2011)
        marketDataContainer = MarketDataContainer.MarketDataContainer()
        marketData = self._pos.marketData(pricingDate=pricingDate, marketId=self._marketId)
        marketDataContainer.add(marketData)
        self._pos.marketDataContainer = marketDataContainer
        #print self._pos.NPV(pricingDate=pricingDate, marketId=self._marketId)
        self.failIf(self._pos.NPV(pricingDate=pricingDate, marketId=self._marketId) <> 12345)
    def test__str__(self):
        self.failIf(str(self._pos) <> "<class 'src.bo.instruments.EquityPosition.EquityPosition'>,EquityPosition,TEST1,100")
    def testExceptionMarketDataMissing(self):
        self.assertRaises(ErrorHandling.MarketDataMissing, self._pos.NPV, Date.Date(1,1,2009))
    def testLoadAndSaveMarketData_TODO(self):
        #curve should never exist
        self._posMarketDataMissing.loadAndSaveMarketData(pricingDate=self._marketDataMissingDate, 
                                                         marketId=self._marketId)
        self.failIf(StockPrice.objects.filter(equity__ticker=self._posMarketDataMissing.secId, 
                                              marketId=self._marketId, 
                                              pricingDate=self._marketDataMissingDate).exists() <> True)
        stockPrice = StockPrice.objects.get(equity__ticker=self._posMarketDataMissing.secId, 
                                            marketId=self._marketId, 
                                            pricingDate=self._marketDataMissingDate)
        stockPrice.delete()
            
def suite():
    return unittest.makeSuite(TestEquityPosition)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testTickerName']
    unittest.main()