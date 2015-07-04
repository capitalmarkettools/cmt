'''
Created on Nov 12, 2009

@author: capitalmarkettools
'''
import unittest
from src.bo.Shift import ShiftCurve
from src.bo.Enum import ShiftType
from src.bo.Date import Date
class Test(unittest.TestCase):

    def setUp(self):
        self.shiftCurve = ShiftCurve()

    def testSetAndStr(self):
        self.shiftCurve.shifts.append((Date(11,11,2009), 0.01))
        self.shiftCurve.shiftType = ShiftType.PERCENTAGE
        
def suite():
    return unittest.makeSuite(Test)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()