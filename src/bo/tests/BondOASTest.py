'''
Created on Sep 9, 2013

@author: Capital Market Tools
'''
import unittest
from src.models import TCBond, BondOAS
from src.bo.Date import Date

class Test(unittest.TestCase):


    def setUp(self):
        self.pricingDate = Date(month=9,day=12,year=2011)
        self.notFoundDate = Date(month=9,day=12,year=2001)
        self.marketId = 'TEST1'
        self.tCBond = TCBond.objects.get(name='TEST1')
        
    def tearDown(self):
        bondOAS = BondOAS.objects.filter(tCBond=self.tCBond, pricingDate=self.notFoundDate,
                                         marketId=self.marketId)
        if bondOAS:
            bondOAS[0].delete()
    
    def testLoadOAS(self):
        bondOAS = BondOAS.objects.get(tCBond=self.tCBond, pricingDate=self.pricingDate,
                                      marketId=self.marketId)
        self.failIf(bondOAS.mid<>0.0012, 'Loaded OAS value incorrect')
        
    def testSaveNewOAS(self):
        bondOAS = BondOAS(tCBond=self.tCBond, pricingDate=self.notFoundDate,
                          marketId=self.marketId, mid=0.01)
        bondOAS.save()
        check = BondOAS.objects.get(tCBond=self.tCBond, pricingDate=self.notFoundDate,
                                    marketId=self.marketId)
        self.failIf(check.mid <> bondOAS.mid, 'Loaded does not match saved oas')
        
    def testSaveExistingOAS(self):
        bondOAS = BondOAS.objects.get(tCBond=self.tCBond, pricingDate=self.pricingDate,
                                      marketId=self.marketId)
        saveOriginal = bondOAS.mid
        bondOAS.mid = 0.1
        bondOAS.save()
        check = BondOAS.objects.get(tCBond=self.tCBond, pricingDate=self.pricingDate,
                                    marketId=self.marketId)
        checkMid = check.mid
        #restore and then check test condition
        bondOAS.mid = saveOriginal
        bondOAS.save()
        self.failIf(checkMid <> 0.1, 'Loaded mid value does not match saved one')
        
def suite():
    return unittest.makeSuite(Test)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()