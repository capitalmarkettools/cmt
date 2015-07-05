'''
Created on Sep 9, 2013

@author: Capital Market Tools
'''
import unittest
from src.bo.Date import Date

class Test(unittest.TestCase):

    def setUp(self):
        self.pricingDate = Date(month=9,day=12,year=2011)
        self.marketId = 'TEST1'
        
    def tearDown(self):
        pass
    
    def testGenerate10Paths(self):
#         vol = SwaptionVolatility(self.pricingDate, self.marketId, ccy, index)
#         bgmVols = SwaptionVolatility.calibrate(list of European Swaptions)
#         bgmModel = BGMModel(bgmVols, yieldCurve, self.pricingDate, self.marketId)
#         randon = RandomNumberGenerator(360*10)
#         paths = bgmModel.generatePaths(10, random)
        self.fail('Not implemented yet')
        
    def testCalibrateToSwaptionDiagonal(self):
#         vol = SwaptionVolatility(self.pricingDate, self.marketId, ccy, index)
#         bgmVols = SwaptionVolatility.calibrate(Bermudan Swaptions)
        self.fail('Not implemented yet')
        
    def testPriceDiscountBond(self):
        self.fail('Not implemented yet')

    def testPriceEuropeanSwaption(self):
        self.fail('Not implemented yet')

    def testPriceBermudanSwaption(self):
        self.fail('Not implemented yet')
           
def suite():
    return unittest.makeSuite(Test)

if __name__ == "__main__":
    unittest.main()