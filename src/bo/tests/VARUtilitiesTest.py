'''
Created on Oct 26, 2009

@author: capitalmarkettools
'''
import unittest
from src.bo import VARUtilities, Date, Enum
from src.bo.static import Calendar

class Test(unittest.TestCase):

    def setUp(self):
        self.timeSteps = VARUtilities.VARTimePeriodsAndSteps()

    def testInit(self):
        self.failIf(self.timeSteps.start <> None, "")
        self.failIf(self.timeSteps.end <> None, "")
        self.failIf(self.timeSteps.timeSteps <> [], "")
        
    def tesenerate_Q_20070301_20090203(self):
        self.timeSteps.generate_Q_20070301_20090203()
        self.failIf(self.timeSteps.start <>  Date.Date(3, 1, 2007), "Error start date")
        self.failIf(self.timeSteps.end <> Date.Date(2, 3, 2009), "Error end date")
        self.failIf(len(self.timeSteps.timeSteps) <> 9, "Error length timeSteps")
        
    def tesenerate_Q_20090625_20110925(self):
        self.timeSteps.generate_Q_20090625_20110925()
        self.failIf(len(self.timeSteps.timeSteps) <> 10, "Error length timeSteps")
    
    def testDateGeneration(self):
        self.timeSteps.generate(Date.Date(1,3,2009), Date.Date(15,3,2009),1, Enum.TimePeriod('D'), Calendar.Target())
        self.failUnlessEqual(len(self.timeSteps.timeSteps), 11, "Generating dates has incorrect number of dates") 

def suite():
    return unittest.makeSuite(Test)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testInit']
    unittest.main()