'''
Created on Nov 8, 2009

@author: capitalmarkettools
'''
import unittest
from src.models import Equity

class Test(unittest.TestCase):
    ''' All StockPrice tests should be done with stock=TEST1 pricingDate=9/12/69 marketId=TEST1 '''
    def setUp(self):
        self.equity = Equity()
    def testEquitySave(self):
        self.equity.ticker = 'TEST1'
        self.equity.save()
    def testEquityLoad(self):
        qs = Equity.objects.filter(ticker='TEST1')
        self.equity = qs[0]
        self.failUnlessEqual(self.equity.ticker, 'TEST1', 'Equity loaded incorrectly') 

def suite():
    return unittest.makeSuite(Test)
if __name__ == "__main__":
    unittest.main()