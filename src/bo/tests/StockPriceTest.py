'''
Created on Nov 8, 2009

@author: capitalmarkettools
'''
import unittest
#import src.bo
#from src.bo import VARUtilities, Enum
from src.bo import Date
#from src.bo.static import Calendar
from src.models import StockPrice, Equity

class Test(unittest.TestCase):
    ''' All StockPrice tests should be done with stock=TEST1 pricingDate=9/12/69 marketId=TEST1 '''
    def setUp(self):
        self.stockPrice = StockPrice()
    def testSP_SetTicker(self):
        equity = Equity()
        equity.ticker = 'TEST1'
        self.stockPrice.equity = equity
        self.stockPrice.pricingDate = Date.Date(month=9,day=12,year=2011)
        self.failUnlessEqual(self.stockPrice.equity.ticker, 'TEST1', 'StockPrice ticker returned wrong value') 
    def testSP_Save(self):
        self.stockPrice.equity = Equity.objects.get(ticker='TEST1')
        self.stockPrice.pricingDate = Date.Date(month=9,day=12,year=2011)
        self.stockPrice.marketId = 'TEST1'
        self.stockPrice.mid = 123.45
        self.stockPrice.save() 
    def testSP_Load(self):
        #Assumes just one Test1 record
        self.stockPrice = StockPrice.objects.get(equity__ticker='TEST1', marketId='TEST1',\
                                                pricingDate=Date.Date(month=9,day=12,year=2011))
        #print self.stockPrice.mid
        self.failUnlessEqual(self.stockPrice.mid, 123.45, 'StockPrice loaded value incorrect') 
    def testSP_Value_SetValue(self):
        self.stockPrice.mid = 10.123
        self.failUnlessEqual(self.stockPrice.mid, 10.123, 'StockPrice value not stored') 
    def testSP_Date_SetDate(self):
        self.stockPrice.date = Date.Date(month=9,day=12,year=2011)
        self.failUnlessEqual(self.stockPrice.date, Date.Date(month=9,day=12,year=2011), 'StockPrice date not stored') 
    def testLargeLoad(self):
        #TODO: Fix test
        pass
#        timeSteps = VARUtilities.VARTimePeriodsAndSteps()
#        timeSteps.generate(Date.Date(2,1,2008), Date.Date(1,3,2008), 
#                           1, Enum.TimePeriod('D').ql(), Calendar.US())
#        self.stockPrice.ticker = 'GOOG'
#        i = 0;
#        for date in timeSteps.timeSteps:
#            self.stockPrice.pricingDate = date
#            self.stockPrice.load()
#            i = i + 1

def suite():
    return unittest.makeSuite(Test)
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test']
    unittest.main()