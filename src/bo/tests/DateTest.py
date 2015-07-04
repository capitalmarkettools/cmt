'''
Created on Oct 23, 2009

@author: capitalmarkettools
'''
import unittest, datetime
from src.bo.Date import Date

class Test(unittest.TestCase):
    "Unit test for Date"
    def setUp(self):
        self.date = Date(day=14, month=5, year=2009)
    def testFromPythonDate(self):
        d = datetime.date(year=2011, month=10, day=15)
        self.date.fromPythonDate(d)
        self.failUnlessEqual(self.date, Date(day=15,month=10,year=2011), 'From Python date fails')
    def testStr(self):
        self.failUnlessEqual(str(self.date), "05/14/2009", "__str__ returns unexpected value")
    def testStr_yyyymmdd(self):
        self.failUnlessEqual(self.date.str_yyyymmdd(), "20090514", "str_yyymmdd() returns unexpected value")
    def test__cmp__(self):
        self.failIf(Date(14,5,2009) <> Date(14,5,2009), "Error in not equal")
        self.failIf(Date(14,5,2009) == Date(14,6,2009), "Error in equal")
        self.failUnless(Date(14,5,2009) == Date(14,5,2009), "Error in not equal")
        self.failUnless(Date(14,5,2009) <> Date(14,6,2009), "Error in equal")
    def test_str_MySQLdb(self):
        #print self.date.str_MySQLdb()
        self.failUnlessEqual(self.date.str_MySQLdb(), "2009-05-14", "str_MySQLdb returns unexpected results")
def suite():
    return unittest.makeSuite(Test)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()