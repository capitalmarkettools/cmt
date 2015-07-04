'''
Created on Dec 15, 2012

@author: Capital Market Tools
'''
import unittest
import QuantLib
from src.bo.instruments.SwapPosition import SwapPosition
from src.bo.MarketDataContainer import MarketDataContainer
from src.bo.Date import Date
from src.bo.static import Calendar
from src.bo.static import Basis
from src.bo.Enum import Index, Currency, Frequency, TimePeriod, Roll
from src.bo import ErrorHandling
from src.models import TCSwap, InterestRateCurve
from datetime import date
class TestSwapPosition(unittest.TestCase):
    '''Unit test of BondPosition
    '''
    def setUp(self):
        self._pricingDate = Date(month=9,day=12,year=2011)
        self._marketId = 'TEST1'
        QuantLib.Settings.instance().evaluationDate = self._pricingDate.ql()
        self._tcSwap = TCSwap(name='Dummy',
                        ccy = Currency('USD'),
                        startDate = date(month=9,day=14,year=2011),
                        endDate = date(month=9,day=14,year=2016),
                        fixedCoupon = 0.01,
                        fixedBasis = Basis.createBasis('30360'),
                        fixedPaymentFrequency = Frequency('S'),
                        fixedPaymentRollRule = Roll('MF'),
                        fixedPaymentCalendar = Calendar.createCalendar('US'),
                        floatingIndex = Index('LIBOR'),
                        floatingIndexTerm = TimePeriod('M'),
                        floatingIndexNumTerms = 3,
                        floatingSpread = 0.0,
                        floatingBasis = Basis.createBasis('30360'),
                        floatingPaymentFrequency = Frequency('Q'),
                        floatingPaymentRollRule = Roll('MF'),
                        floatingPaymentCalendar = Calendar.createCalendar('US'),
                        floatingResetFrequency = Frequency('Q'),
                        floatingResetRollRule = Roll('MF'),
                        floatingResetCalendar = Calendar.createCalendar('US'))
        self._pos = SwapPosition(amount=1000000, tcSwap=self._tcSwap)
    def testNPV(self):
        marketDataContainer = MarketDataContainer()
        marketData = self._pos.marketData(self._pricingDate, self._marketId)
        marketDataContainer.add(marketData)
        self._pos.setMarketDataContainer(marketDataContainer)
    #    print round(self._pos.NPV(self._pricingDate, self._marketId),2)
        self.failIf(round(self._pos.NPV(self._pricingDate, self._marketId),2) <> -5044.78)
#    def test__str__(self):
#        self.failIf(str(self._pos) <> '<<class \'src.bo.instruments.BondPosition.BondPosition\'>,TEST1,100>')
    def testFairRate(self):
        marketDataContainer = MarketDataContainer()
        marketData = self._pos.marketData(self._pricingDate, self._marketId)
        marketDataContainer.add(marketData)
        self._pos.setMarketDataContainer(marketDataContainer)
   #     print round(self._pos.fairRate(self._pricingDate, self._marketId),2)
        self.failIf(round(self._pos.fairRate(self._pricingDate, self._marketId),2) <> 0.01)
    def testFairSpread(self):
        marketDataContainer = MarketDataContainer()
        marketData = self._pos.marketData(self._pricingDate, self._marketId)
        marketDataContainer.add(marketData)
        self._pos.setMarketDataContainer(marketDataContainer)
  #      print round(self._pos.fairSpread(self._pricingDate, self._marketId),2)
        self.failIf(round(self._pos.fairSpread(self._pricingDate, self._marketId),2) <> 0.0)
    def testExceptionMarketDataMissing(self):
        self.assertRaises(ErrorHandling.MarketDataMissing,
                          self._pos.NPV, Date(1,1,2009))
    def testPriceWith2Curves(self):
        marketDataContainer = MarketDataContainer()
        marketData = self._pos.marketData(self._pricingDate, self._marketId)
#        print marketData[0].buildZeroCurve().nodes()
        marketDataContainer.add(marketData)
        self._pos.setMarketDataContainer(marketDataContainer)
        price1 = round(self._pos.NPV(self._pricingDate, self._marketId),5)
 #       print price1
        marketData[0].shift(0.01)
#        print marketData[0].buildZeroCurve().nodes()
        marketDataContainer1 = MarketDataContainer()
        marketDataContainer1.add(marketData)
        self._pos.setMarketDataContainer(marketDataContainer1)
        #add dirty flag to position to run setupql again. add add marketdatacontainer method
        price2 = round(self._pos.NPV(self._pricingDate, self._marketId),5)
#        print price2
        self.failIf(price1 == price2)
        
    def testLoadAndSaveMarketData_TODO(self):
        #curve should never exist
        self._pos.loadAndSaveMarketData(pricingDate=Date(1,1,2009), 
                                        marketId=self._marketId)
        #now, curve should exist
        irCurve = InterestRateCurve()
        irCurve.ccy = Currency('USD')
        irCurve.index = Index('LIBOR')
        irCurve.term = 'M'
        irCurve.numTerms = 3
        irCurve.pricingDate = Date(1,1,2009)
        irCurve.marketId = self._marketId
        irCurve.load()
        #now, delete again so that next test will work
        irCurve.delete()
def suite():
    return unittest.makeSuite(TestSwapPosition)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testTickerName']
    unittest.main()