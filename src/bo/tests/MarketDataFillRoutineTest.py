'''
Created on Aug 29, 2013

@author: Capital Market Tools
'''
import unittest
from src.bo.Date import Date

class Test(unittest.TestCase):

    def setUp(self):
        self._asOf = Date(month=9,day=12,year=2011)
        self._startDate = Date(month=9,day=12,year=2011)
        self._endDate = Date(month=9,day=12,year=2011)
        self._marketId = 'TEST1'

#Add portfolio
#setup. create equity prices with gaps
#test1: ake sure to fill gaps
#delete equity prices

    def testFillOneDate(self):
        self.fail("Not implemented yet")
    
def suite():
    return unittest.makeSuite(Test)

if __name__ == "__main__":
    unittest.main()