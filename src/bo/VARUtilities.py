'''
Created on Oct 13, 2009

@author: capitalmarkettools
'''
from src.bo import Date, Enum
from src.bo.static import Calendar

class VARTimePeriodsAndSteps(object):
    """Time steps used for Historical VAR"""
    def __init__(self):
        self.start = None
        self.end = None
        self.timeSteps = []
    def generate_Q_20070301_20090203(self):
        self.start = Date.Date(3, 1, 2007)
        self.end = Date.Date(2, 3, 2009)
        self.timeSteps = [ self.start,
                           Date.Date(1, 6, 2007),
                           Date.Date(4, 9, 2007),
                           Date.Date(3, 12, 2007),
                           Date.Date(3, 3, 2008),
                           Date.Date(2, 6, 2008),
                           Date.Date(2, 9, 2008),
                           Date.Date(1, 12, 2008),
                           self.end ]

    def generate_Q_20090625_20110925(self):
        self.start = Date.Date(25,6,2009)
        self.end = Date.Date(26,9,2011)
        self.timeSteps = [ self.start,
                           Date.Date(25,9,2009),
                           Date.Date(28,12,2009),
                           Date.Date(25,3,2010),
                           Date.Date(25,6,2010),
                           Date.Date(27,9,2010),
                           Date.Date(27,12,2010),
                           Date.Date(25,3,2011),
                           Date.Date(27,6,2011),
                           self.end ]
        
    def generate(self, start, end, num, term, calendar):
        """Generate timeSteps
        Inputs: Start, End, NumDays, Term, Calendar
        term should be Enum.TimePeriod
        """
        self.start = start
        self.end = end
        newDate = start
        while newDate <= self.end:
            self.timeSteps.append(newDate)
            newDate = calendar.advance(date=newDate,num=num,term=term)
    def __str__(self):
        s = ''
        for t in self.timeSteps:
            s = s + str(t) + '\n'
        return s
           
def main():
    timeSteps = VARTimePeriodsAndSteps()
    print 'timeSteps: ' + str(timeSteps)
    timeSteps.generate(start=Date.Date(1,1,2009), end=Date.Date(10,1,2009), num=1, 
                       term=Enum.TimePeriod('D'), calendar=Calendar.Target())
    for index, i in enumerate(timeSteps.timeSteps):
        print index, i
                       
if __name__ == "__main__":
    main()