'''
Created on Nov 15, 2009

@author: capitalmarkettools
'''
import unittest
from src.bo import Date, MarketDataContainer
from src.models import StockPrice, Equity,Portfolio, BondOAS, TCBond
from src.bo.instruments.EquityPosition import EquityPosition

class Test(unittest.TestCase):


    def setUp(self):
        self.marketDataContainer = MarketDataContainer.MarketDataContainer()
        self.pricingDate = Date.Date(month=9,day=12,year=2011)
        self.marketId = 'TEST1'
    def testCreate(self):
        portfolio =Portfolio()
        portfolio.addPosition(EquityPosition(amount=100,secId='TEST1'))

        self.marketDataContainer.create(portfolio=portfolio, 
                                        pricingDate=Date.Date(month=9,day=12,year=2011), 
                                        marketId='TEST1')

    def testFindStockPriceSuccess(self):
        #create stockprice, add it to coainer and find it again
        e = Equity()
        e.ticker = 'TEST1'
        s1 = StockPrice()
        s1.equity = e
        s1.pricingDate = self.pricingDate
        s1.marketId = self.marketId
        s1.mid = 1.234
        l = []
        l.append(s1)
        self.marketDataContainer.add(l)
        self.failIf(self.marketDataContainer.find(s1) == None)
        
    def testFindStockPriceFail(self):
        #create stockprice, add it to coainer and find it again
        e = Equity()
        e.ticker = 'TEST1'
        s1 = StockPrice()
        s1.equity = e
        s1.pricingDate = self.pricingDate
        s1.marketId = self.marketId
        s1.mid = 1.234
        l = []
        l.append(s1)
        self.marketDataContainer.add(l)
        s2 = StockPrice()
        s2.equity = e
        s2.pricingDate = Date.Date(month=9,day=13,year=2011)
        s2.marketId = self.marketId
        s2.mid = 1.234
        self.failIf(self.marketDataContainer.find(s2) <> None)
               
    def testFindBondOAS(self):
        bondOAS = BondOAS(pricingDate=self.pricingDate, marketId = self.marketId,
                          tCBond=TCBond.objects.get(name='TEST1'))
        self.marketDataContainer.add([bondOAS])
        self.failIf(self.marketDataContainer.find(bondOAS) == None)

    def testFindBondOASFail(self):
        bondOAS = BondOAS(pricingDate=self.pricingDate, marketId = self.marketId,
                          tCBond=TCBond.objects.get(name='TEST1'))
        self.failIf(self.marketDataContainer.find(bondOAS) <> None)
    
def suite():
    return unittest.makeSuite(Test)
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()