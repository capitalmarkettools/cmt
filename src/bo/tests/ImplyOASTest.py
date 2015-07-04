'''
Created on Aug 29, 2013

@author: Capital Market Tools
'''
import unittest
from src.bo.calculators.ImplyOAS import ImplyOAS
from src.models import TCBond
from src.bo.Date import Date

class Test(unittest.TestCase):

    def setUp(self):
        self.pricingDate = Date(month=9,day=12,year=2011)
        self.marketId = 'TEST1'
        self.tCBond = TCBond.objects.get(name='TEST1')
    
    def testOneBondPriceToOAS(self):
        imply = ImplyOAS(pricingDate=self.pricingDate, 
                         marketId=self.marketId,tCBond=self.tCBond)
        oas = imply.implyOAS(price=100.0)
        #print round(oas,5)
        self.failIf(round(oas,5) <> 0.00125, "Imply calculation does not match expected oas")
    
def suite():
    return unittest.makeSuite(Test)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testImplyOAS']
    unittest.main()