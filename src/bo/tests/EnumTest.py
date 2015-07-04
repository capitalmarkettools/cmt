'''
Created on Nov 12, 2009

@author: capitalmarkettools
'''
import unittest
from src.bo import Enum
from src.bo.Enum import Roll
import QuantLib

class Test(unittest.TestCase):

    def testShiftType_ABSOLUTE(self):
        self.failUnless('%s' % Enum.ShiftType.ABSOLUTE == '<class><className>type</className><data>name>absolute</name></data></class>', 'Enum.ShiftType.ABSOLUTE incorrect')
    def testShiftType_PERCENTAGE(self):
        self.failUnless('%s' % Enum.ShiftType.PERCENTAGE == '<class><className>type</className><data>name>percentage</name></data></class>', 'Enum.ShiftType.PERCENTAGE incorrect')
    def testDaily(self):
        self.failUnless(Enum.Frequency('D').ql() == 365, '')
    def testDays(self):
        self.failUnless(Enum.TimePeriod('D').ql() == 0, '')
    def testBasicFunctionsRoll(self):
        mf = Roll(value='MF')
        self.failIf(str(mf) <> "MF", "Roll('MF') cannot be constructed and convert to string correctly")
        mf = Roll('F')
        self.failIf(str(mf) <> "F", "Roll('F') cannot be constructed and convert to string correctly")
        self.failUnless( mf == Roll('F'), "Equality does not work")
        self.failUnless( mf <> Roll('MF'), "InEquality does not work")
        self.failUnless(mf.ql() == QuantLib.Following, 'QuantLib mapping failed')
        
def suite():
    return unittest.makeSuite(Test)
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()