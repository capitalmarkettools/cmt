'''
Created on Jul 21, 2013

@author: Capital Market Tools
'''

import sys
import datetime
from src.bo.Date import Date
from src.models import InterestRateCurve, InterestRate, StockPrice, BondOAS

class ShiftInterestRateCurve(object):
    '''
    Shifts interest rate curve by x basis points
    '''
    
    def __init__(self, date = None, marketId = None, shift = None):
        if shift > 0.01 or shift < -0.01:
            print "Warning. Shifting rates by more than 1%. Shift specified is " + str(shift)
        curves = InterestRateCurve.objects.filter(pricingDate = date, marketId = marketId)
        for curve in curves:
            curve.loadRates()
            
            for rate in curve.getRates():
                rate.mid = rate.mid + shift
            
            curve.save()

def main():
    print "Shifting Start"
    if len(sys.argv) != 4:
        print "Needs 3 arguments: Date, MarketId, Shift in decimal"
        exit(-1)
    else:
        fromDate = Date()
        fromDate.fromPythonDate(datetime.datetime.strptime(sys.argv[1],"%Y%m%d").date())
        shifter = ShiftInterestRateCurve(date = fromDate, marketId = sys.argv[2], shift = float(sys.argv[3]))

    print "Copying Done"
if __name__ == "__main__":
    main()