'''
Created on Oct 26, 2009

@author: capitalmarkettools
'''
import unittest
import QuantLib
from src.bo.instruments import EquityPosition, BondPosition
from src.bo.instruments.FinancialInstrument import CreatePosition
from src.bo import Date, MarketDataContainer
from src.models import Portfolio

class Test(unittest.TestCase):

    def setUp(self):
        self.pricingDate = Date.Date(month=9,day=12,year=2011)
        self.marketId = 'TEST1'
        QuantLib.Settings.instance().evaluationDate = self.pricingDate.ql()
        self.portfolio = Portfolio()

    def testOneBondAndOneEquity(self):
        marketDataContainer = MarketDataContainer.MarketDataContainer()
        stock = EquityPosition.EquityPosition(100,'TEST1')
        marketDataContainer.add(stock.marketData(pricingDate=self.pricingDate, marketId=self.marketId))
        stock.marketDataContainer = marketDataContainer
        bond = BondPosition.BondPosition(10000, 'TEST1')
        marketDataContainer.add(bond.marketData(self.pricingDate, self.marketId))
        bond.marketDataContainer = marketDataContainer
        portfolio = Portfolio()
        portfolio.addPosition(stock)
        portfolio.addPosition(bond)
#        print stock.NPV(self.pricingDate, self.marketId)
 #       print bond.NPV(self.pricingDate, self.marketId)
        #print round(portfolio.NPV(pricingDate=self.pricingDate, marketId=self.marketId),2)
        self.failIf(round(portfolio.NPV(pricingDate=self.pricingDate, marketId=self.marketId),2) <> 1012696.1)
        
    def testNPVPortfolioTEST1(self):
        portfolio = Portfolio.objects.get(name='TEST1',user='test1')
        modelPositions = portfolio.modelposition_set.filter(asOf=self.pricingDate)
        for modelPosition in modelPositions:
            position = CreatePosition(modelPosition)
            portfolio.addPosition(position)
        marketDataContainer = MarketDataContainer.MarketDataContainer()
        for position in portfolio.positions:
#            print position
            marketDataContainer.add(position.marketData(pricingDate=self.pricingDate, marketId=self.marketId))
            position.marketDataContainer = marketDataContainer
            
 #       print portfolio.NPV(pricingDate=self.pricingDate, marketId=self.marketId)
        self.failIf(round(portfolio.NPV(pricingDate=self.pricingDate, marketId=self.marketId),2) <> 76669.51)
        
def suite():
    return unittest.makeSuite(Test)
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()