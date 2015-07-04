'''
Created on Sep 9, 2013

@author: Capital Market Tools
'''
import unittest
from src.bo.calculators.TimeSeriesNPVCalculator import TimeSeriesNPVCalculator, TimeSeriesNPVCalculatorParameters
from src.bo.Date import Date
from src.models import Portfolio

class Test(unittest.TestCase):

    def setUp(self):
        self._pricingDate = Date(month=9,day=12,year=2011)
        self._marketId = 'TEST1'
        self._portfolio = Portfolio.objects.get(name='TEST1',user='test1')
    def tearDown(self):
        pass
    
    def testTimeSeriesOneDate(self):
        parameters = TimeSeriesNPVCalculatorParameters(start=self._pricingDate,
                                                       end=self._pricingDate,
                                                       marketId=self._marketId,
                                                       portfolios=[self._portfolio])
        p = TimeSeriesNPVCalculator(parameters=parameters)
        p.calc()
        result = p.results()[0]
        self.assertEqual(result[0],self._pricingDate,'Result Date incorrect')
#        print result
        self.assertEqual(round(result[1],2),76669.51,'Result NPV incorrect')
                         
def suite():
    return unittest.makeSuite(Test)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()