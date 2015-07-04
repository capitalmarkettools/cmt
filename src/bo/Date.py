'''
Created on Oct 10, 2009

@author: capitalmarkettools
'''
import QuantLib
from datetime import date, timedelta
from src.bo import cmt

def createPythonDateFromQLDate(qlDate):
    return date(year=qlDate.year(), month=qlDate.month(),day=qlDate.dayOfMonth())
    
def createQLDateFromPythonDate(pDate):
    return QuantLib.Date(pDate.day, pDate.month, pDate.year)
   
class Date(cmt.cmt):
    '''
    Date class. Uses QuantLib date class
    This class must be used in all application code. The conversion to python dates or sybase 
    dates must happen as late as possible
    '''
    #TODO: Fix this convention to american convention to have month first
    def __init__(self, day=1, month=1, year=2000, pythonDate=None):
        """Input: Day, Month, Year"""
        if pythonDate:
            self._date = pythonDate
        else:
            self._date = date(day=day, month=month, year=year)
    def dayOfMonth(self):
        return self._date.day
    def month(self):
        return self._date.month
    def year(self):
        return self._date.year
    def str_yyyymmdd(self):
        """Used to convert to string used by ystockquote.py"""
        return str(self._date.year)+"%02d"%self._date.month+"%02d"%self._date.day
    def str_MySQLdb(self):
        """Used to convert to string use in Date type of MySQLdb"""
        return "%d-%02d-%02d" % (self._date.year, self._date.month, self._date.day)
    def __repr__(self):
        return "%02d/%02d/%d" % (self._date.month, self._date.day,self._date.year)
    def __str__(self):
#        return str(self._date)
        return "%02d/%02d/%d" % (self._date.month, self._date.day,self._date.year)
    def __cmp__(self, other):
        ''' Convention is that any date is larger than None '''
        if other.__class__ <> Date:
            return 1
        if self._date.year > other.year():
            return 1
        elif self._date.year < other.year():
            return -1
        elif self._date.month > other.month():
            return 1
        elif self._date.month < other.month():
            return -1
        elif self._date.day > other.dayOfMonth():
            return 1
        elif self._date.day < other.dayOfMonth():
            return -1
        else:
            return 0

    def fromPythonDate(self, date):
        self._date = date
        
    def toPythonDate(self):
        return self._date
        
    def isoformat(self):
        return self._date.isoformat()
    
    def ql(self):
        return createQLDateFromPythonDate(self._date)

    def nextDay(self):
        self._date += timedelta(days=1)
        
def main():
    today = Date(16, 8, 2009)
    print '%s' % today
    newDate = date(2009,10,10)
    print newDate
    print type(newDate)
    if newDate == today:
        print 'y'
    else:
        print 'n'
    dateList = [Date(16,8,2009), Date(16,8,2009),Date(17,8,2009)]
    for d in dateList:
        for dd in dateList:
            print d == dd
    import json
    print json.dumps(today)
if __name__ == "__main__":
    main()