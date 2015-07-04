'''
Created on Nov 11, 2009

@author: capitalmarkettools
'''
import Date
from src.bo.Enum import ShiftType
from src.bo import cmt

class ShiftCurve(cmt.cmt):
    """Implements shift curve"""
    def __init__(self):
        """Sets all attributes to None"""
        #shift are tuples of Date and float
        #TODO: do I need to make the dates generic?
        self.shifts = []
        self.shiftType = None
    def addShift(self, date, value):
        '''
        adds shift without checking if it already exists
        '''
        self.shifts.append((date, value))
    
def main():
    print 'Start'
    shift = ShiftCurve()
    shift.shifts.append((Date.Date(11,11,2009), 0.01))
    shift.shifts.append((Date.Date(11,11,2010), 0.01))
    shift.shiftType = ShiftType.PERCENTAGE
    print shift 
    print 'End'     
if __name__ == "__main__":
    main() 
        