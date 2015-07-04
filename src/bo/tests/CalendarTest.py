'''
Created on Oct 27, 2009

@author: Tim Glauner
'''
import unittest
from src.bo import Date, Enum, ErrorHandling
from src.bo.static import Calendar
from src.bo.static.Calendar import createCalendar

class Test(unittest.TestCase):
    def setUp(self):
        self.calendarTarget = Calendar.Target()
        self.calendarUS = Calendar.US()
    def test_advanceTarget(self):
        date = Date.Date(15, 1, 2009)
        date = self.calendarTarget.advance(date,1,Enum.TimePeriod('D'))
        self.failIf(date <> Date.Date(16,1,2009), "Error advancing one business day")
        date = self.calendarTarget.advance(date,1,Enum.TimePeriod('D'))
        self.failIf(date <> Date.Date(19,1,2009), "Error advancing one business day over weekend")
    def test_advanceUS(self):
        date = Date.Date(15, 1, 2009)
        date = self.calendarUS.advance(date,1,Enum.TimePeriod('D'))
        self.failIf(date <> Date.Date(16,1,2009), "Error advancing one business day")
        date = self.calendarUS.advance(date,1,Enum.TimePeriod('D'))
        #1/19/09 is holiday in US
        self.failIf(date <> Date.Date(20,1,2009), "Error advancing one business day over weekend")
    def test_20070102_US(self):
        date = Date.Date(1,1,2007)
        self.failIf(self.calendarUS.isBusinessDay(date.ql()) <> False, 'Error isBusinessDay')
        date = Date.Date(2,1,2007)
        self.failIf(self.calendarUS.isBusinessDay(date.ql()) <> True, 'Error isBusinessDay')
    def test_create(self):
        c = createCalendar('US')
        self.failIf(c.__class__ <> Calendar.US, 'Error')
        c = createCalendar('TARGET')
        self.failIf(c.__class__ <> Calendar.Target, 'Error')
        self.assertRaises(ErrorHandling.OtherException, createCalendar,'bad')
        
def suite():
    return unittest.makeSuite(Test)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()