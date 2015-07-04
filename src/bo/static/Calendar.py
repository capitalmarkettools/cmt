'''
Created on Oct 26, 2009

@author: capitalmarkettools
'''
import QuantLib
from src.bo import Enum, Date, ErrorHandling, cmt

class Calendar(cmt.cmt):
    choices=(('US','US'),('TARGET','Target'),)
    
    def __init__(self):
        super(Calendar, self).__init__()

    def __eq__(self, value):
        #TODO: Not sure how to fix this
        if value is None:
            return False
        return True
    def __ne__(self, value):
        return not self == value
    
    #TODO: LOW: Remove hardcoding of 20 for length
    def __len__(self):
        return 20

    def DBString(self):
        return None
    
    def __str__(self):
        return self.DBString()
    
    def ql(self):
        return self
    
class Target(QuantLib.TARGET, Calendar):
    """Inherited from QuantLib.TARGET"""
    def __init__(self):
        Calendar.__init__(self)
        QuantLib.TARGET.__init__(self)
    def advance(self, date, num, term):
        """Adds number of terms to date
        Input: Date, int, term (term is TimePeriod)
        """
        qDate = QuantLib.Date(date.dayOfMonth(), date.month(), date.year())
        #need to map timePeriod to ql()
        nqDate = super(Target,self).advance(qDate, num, term.ql())
        return Date.Date(nqDate.dayOfMonth(), nqDate.month(), nqDate.year())
    def DBString(self):
        return 'TARGET'
    def __eq__(self, value):
        #TODO: Not sure how to fix this
        if value is None:
            return False
        return True
    def __ne__(self, value):
        return not self == value
    def __str__(self):
        return self.DBString()
    
class US(QuantLib.UnitedStates, Calendar):
    """Inherited from QuantLib.TARGET"""
    def __init__(self):
        Calendar.__init__(self)
        QuantLib.UnitedStates.__init__(self)
        holiday = Date.Date(21,3,2008)
        self.addHoliday(Date.Date(21,3,2008).ql())
        self.addHoliday(Date.Date(1,5,2008).ql())
        self.addHoliday(Date.Date(22,4,2011).ql())
    def advance(self, date, num, term):
        """Adds number of terms to date
        Input: Date, int, term (term is TimePeriod)
        """
        qDate = QuantLib.Date(date.dayOfMonth(), date.month(), date.year())
        #need to map timePeriod to ql()
        nqDate = super(US,self).advance(qDate, num, term.ql())
        return Date.Date(nqDate.dayOfMonth(), nqDate.month(), nqDate.year())
    def DBString(self):
        return 'US'
    def __eq__(self, value):
        #TODO: Not sure how to fix this
        if value is None:
            return False
        return True
    def __ne__(self, value):
        return not self == value
    def __str__(self):
        return self.DBString()

def createCalendar(s):
    if s == 'TARGET':
        return Target()
    elif s == 'US':
        return US()
    else:
        raise ErrorHandling.OtherException()
    
def main():
    calendar = Target()
    print "%s" % calendar.advance(Date.Date(1,1,2009), 2, Enum.TimePeriod('D').ql())
if __name__ == "__main__":
    main()
    
    