'''
Created on Sep 9, 2013

@author: Capital Market Tools
'''
import unittest
from src.bo.Date import Date
from src.bo.Enum import Index, Currency, TimePeriod
from src.models import SwaptionVolatilitySurface, SwaptionVolatility

class Test(unittest.TestCase):
    '''
    No test to amend the volatilities for now
    '''
    
    def setUp(self):
        self.pricingDate = Date(month=9,day=12,year=2011)
        self.marketId = 'TEST1'
        
    def tearDown(self):
        pass
    
    def testCreateSurfaceAndVolatility(self):
        vols = SwaptionVolatilitySurface(ccy=Currency('USD'), index = Index('LIBOR'), term = 'M', 
                                         numTerms = 3, pricingDate = self.pricingDate,
                                         marketId = self.marketId)
        volPoints = []
        volPoints.append(SwaptionVolatility(expiryTerm=TimePeriod('Y'), expiryNumTerms=1, underlyingTerm=TimePeriod('Y'),
                                 underlyingNumTerms=3, mid=0.40, surface=vols))
        volPoints.append(SwaptionVolatility(expiryTerm=TimePeriod('Y'), expiryNumTerms=3, underlyingTerm=TimePeriod('Y'),
                                 underlyingNumTerms=3, mid=0.45, surface=vols))
        volPoints.append(SwaptionVolatility(expiryTerm=TimePeriod('Y'), expiryNumTerms=1, underlyingTerm=TimePeriod('Y'),
                                 underlyingNumTerms=5, mid=0.5, surface=vols))
        volPoints.append(SwaptionVolatility(expiryTerm=TimePeriod('Y'), expiryNumTerms=3, underlyingTerm=TimePeriod('Y'),
                                 underlyingNumTerms=5, mid=0.55, surface=vols))
        vols.addVolatilities(volPoints)
        #check vol point
        self.failUnlessAlmostEqual(0.4, vols.getValue(expiryTerm = TimePeriod('Y'), expiryNumTerms = 1, underlyingTerm = TimePeriod('Y'),
                                                      underlyingNumTerms = 3))
        self.failUnlessAlmostEqual(0.45, vols.getValue(expiryTerm = TimePeriod('Y'), expiryNumTerms = 3, underlyingTerm = TimePeriod('Y'),
                                                       underlyingNumTerms = 3))
        self.failUnlessAlmostEqual(0.5, vols.getValue(expiryTerm = TimePeriod('Y'), expiryNumTerms = 1, underlyingTerm = TimePeriod('Y'),
                                                      underlyingNumTerms = 5))
        self.failUnlessAlmostEqual(0.55, vols.getValue(expiryTerm = TimePeriod('Y'), expiryNumTerms = 3, underlyingTerm = TimePeriod('Y'),
                                                       underlyingNumTerms = 5))
        #check interpolated vol point
        self.failUnlessAlmostEqual(0.425, vols.getValue(expiryTerm = TimePeriod('Y'), expiryNumTerms = 2, underlyingTerm = TimePeriod('Y'),
                                                        underlyingNumTerms = 3))
        self.failUnlessAlmostEqual(0.45, vols.getValue(expiryTerm = TimePeriod('Y'), expiryNumTerms = 1, underlyingTerm = TimePeriod('Y'),
                                                       underlyingNumTerms = 4))
        self.failUnlessAlmostEqual(0.475, vols.getValue(expiryTerm = TimePeriod('Y'), expiryNumTerms = 2, underlyingTerm = TimePeriod('Y'),
                                                         underlyingNumTerms = 4))
        
    def testLoad(self):
        vols = SwaptionVolatilitySurface(ccy=Currency('USD'), index = Index('LIBOR'), term = 'M', 
                                         numTerms = 3, pricingDate = self.pricingDate,
                                         marketId = self.marketId)
        vols.load()
        
    def testSave(self):
        vols = SwaptionVolatilitySurface(ccy=Currency('USD'), index = Index('LIBOR'), term = 'M', 
                                         numTerms = 3, pricingDate = self.pricingDate,
                                         marketId = self.marketId)
        vols.load()
        vols.save()
        
    def testGet2Yinto4Y(self):
        vols = SwaptionVolatilitySurface(ccy=Currency('USD'), index = Index('LIBOR'), term = 'M', 
                                         numTerms = 3, pricingDate = self.pricingDate,
                                         marketId = self.marketId)
        vols.load()
        self.failUnlessAlmostEqual(0.475, vols.getValue(expiryTerm = TimePeriod('Y'), expiryNumTerms = 2, underlyingTerm = TimePeriod('Y'),
                                                         underlyingNumTerms = 4))

        #Add extrapolation tests if needed
def suite():
    return unittest.makeSuite(Test)

if __name__ == "__main__":
    unittest.main()