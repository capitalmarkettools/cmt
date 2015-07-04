'''
Created on Nov 9, 2012

@author: Capital Market Tools
'''

import fred
from src.bo import ErrorHandling, Date, Enum
from src.bo.decorators import log
from src.models import InterestRateCurve, InterestRate
class FREDLoader(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
        fred.key('e732114c863993dcb376dac62f9e5473')

    def convertTermNumTermToLiborSeries(self, term, numTerm):
        if term == 'M':
            if numTerm == 1:
                return 'DED1'
            elif numTerm == 3:
                return 'DED3'
            elif numTerm == 6:
                return 'DED6'
        elif term == 'Y':
            if numTerm == 1:
                return 'DSWP1'
            elif numTerm == 2:
                return 'DSWP2'
            elif numTerm == 3:
                return 'DSWP3'
            elif numTerm == 4:
                return 'DSWP4'
            elif numTerm == 5:
                return 'DSWP5'
            elif numTerm == 7:
                return 'DSWP7'
            elif numTerm == 10:
                return 'DSWP10'
            elif numTerm == 30:
                return 'DSWP30'
        raise ErrorHandling.OtherException('Wrong term or numTerm %s/%s' % (term, numTerm))
            
    def convertFREDDatetoDate(self, fDate):
        '''converts FRED date to Date date
        '''
        items = fDate.split('-')
        year = int(items[0])
        month = int(items[1])
        day = int(items[2])
        return Date.Date(day=day, month=month, year=year)
    
    def loadAllLiborRates(self, term, numTerm):
        ''' 
        loads timeSeries of rates for one instrument return dictionary with dates and values
        if value is '.' then previous value is taken
        '''
        series = self.convertTermNumTermToLiborSeries(term, numTerm)
        values = fred.observations(series)['observations']['observation']
        datesRatesVector = {}
        prevValue = 0.0
        for value in values:
            badValue = False
            try:
                float(value['value'])
            except ValueError:
                badValue = True
#            print str(numTerm)+str(term)+' '+str(badValue)+' '+str(value['date'])+' '+str(value['value']) + ' ' +str(prevValue)
            if badValue:
                datesRatesVector[value['date']] = prevValue
            else:
                datesRatesVector[value['date']] = value['value']
                prevValue = value['value']
        return datesRatesVector
    
    def loadDatesForLiborRates(self, term, numTerm):
        series = self.convertTermNumTermToLiborSeries(term, numTerm)
        values = fred.observations(series)['observations']['observation']
        dates = []
        for value in values:
            dates.append(value['date'])
        return dates
    
    @log
    def createAndSaveCurve(self, pricingDate, marketId, r1m, r3m, r6m, r1y, r2y, r3y, r4y, r5y, r7y, r10y, r30y):
        ''' 
        creates specific Libor curve and saves it with
        ''' 
        curve = InterestRateCurve(ccy='USD', index=Enum.Index('LIBOR'), 
                                  term=Enum.TimePeriod('M'), numTerms=3,
                                  pricingDate=pricingDate, marketId=marketId)
        m1 = InterestRate(type='Deposit', term=Enum.TimePeriod('M'), numTerms=1, mid=float(r1m)/100.0, curve=curve)
        m3 = InterestRate(type='Deposit', term=Enum.TimePeriod('M'), numTerms=3, mid=float(r3m)/100.0, curve=curve)
        m6 = InterestRate(type='Deposit', term=Enum.TimePeriod('M'), numTerms=6, mid=float(r6m)/100.0, curve=curve)
        y1 = InterestRate(type='Swap', term=Enum.TimePeriod('Y'), numTerms=1, mid=float(r1y)/100.0, curve=curve)
        y2 = InterestRate(type='Swap', term=Enum.TimePeriod('Y'), numTerms=2, mid=float(r2y)/100.0, curve=curve)
        y3 = InterestRate(type='Swap', term=Enum.TimePeriod('Y'), numTerms=3, mid=float(r3y)/100.0, curve=curve)
        y4 = InterestRate(type='Swap', term=Enum.TimePeriod('Y'), numTerms=4, mid=float(r4y)/100.0, curve=curve)
        y5 = InterestRate(type='Swap', term=Enum.TimePeriod('Y'), numTerms=5, mid=float(r5y)/100.0, curve=curve)
        y7 = InterestRate(type='Swap', term=Enum.TimePeriod('Y'), numTerms=7, mid=float(r7y)/100.0, curve=curve)
        y10 = InterestRate(type='Swap', term=Enum.TimePeriod('Y'), numTerms=10, mid=float(r10y)/100.0, curve=curve)
        y30 = InterestRate(type='Swap', term=Enum.TimePeriod('Y'), numTerms=30, mid=float(r30y)/100.0, curve=curve)
        curve.addRate(m1)
        curve.addRate(m3)
        curve.addRate(m6)
        curve.addRate(y1)
        curve.addRate(y2)
        curve.addRate(y3)
        curve.addRate(y4)
        curve.addRate(y5)
        curve.addRate(y7)
        curve.addRate(y10)
        curve.addRate(y30)
#        curve.printCurve()
        curve.save()
       
    def loadAllLiborCurves(self, marketId):
        lib1m = self.loadAllLiborRates('M', 1)
        lib3m = self.loadAllLiborRates('M', 3)
        lib6m = self.loadAllLiborRates('M', 6)
        lib1y = self.loadAllLiborRates('Y', 1)
        lib2y = self.loadAllLiborRates('Y', 2)
        lib3y = self.loadAllLiborRates('Y', 3)
        lib4y = self.loadAllLiborRates('Y', 4)
        lib5y = self.loadAllLiborRates('Y', 5)
        lib7y = self.loadAllLiborRates('Y', 7)
        lib10y = self.loadAllLiborRates('Y', 10)
        lib30y = self.loadAllLiborRates('Y', 30)
        dates = self.loadDatesForLiborRates('Y', 5)
#        counter = 0
        for date in dates:
 #           counter = counter + 1
#            print 'Processing item ' + str(counter) + ': ' + date + ' with id ' + marketId
 #           print 'lib1y: ' + str(lib1y)
            self.createAndSaveCurve(self.convertFREDDatetoDate(date),
                                    marketId,
                                    lib1m[date],
                                    lib3m[date],
                                    lib6m[date],
                                    lib1y[date],
                                    lib2y[date],
                                    lib3y[date],
                                    lib4y[date],
                                    lib5y[date],
                                    lib7y[date],
                                    lib10y[date],
                                    lib30y[date])
      #      if counter > 5:
    #            break

    def loadLiborCurvesForSpecificDates(self, marketId=None, datesToLoadFor=None):
        if (marketId==None or datesToLoadFor==None):
            raise ErrorHandling.ParameterException("marketId and datesToLoadFor must be passed")
        lib1m = self.loadAllLiborRates('M', 1)
        lib3m = self.loadAllLiborRates('M', 3)
        lib6m = self.loadAllLiborRates('M', 6)
        lib1y = self.loadAllLiborRates('Y', 1)
        lib2y = self.loadAllLiborRates('Y', 2)
        lib3y = self.loadAllLiborRates('Y', 3)
        lib4y = self.loadAllLiborRates('Y', 4)
        lib5y = self.loadAllLiborRates('Y', 5)
        lib7y = self.loadAllLiborRates('Y', 7)
        lib10y = self.loadAllLiborRates('Y', 10)
        lib30y = self.loadAllLiborRates('Y', 30)
        dates = self.loadDatesForLiborRates('Y', 5)
#        counter = 0
        for date in dates:
            if self.convertFREDDatetoDate(date) in datesToLoadFor:
 #           counter = counter + 1
#            print 'Processing item ' + str(counter) + ': ' + date + ' with id ' + marketId
 #           print 'lib1y: ' + str(lib1y)
                self.createAndSaveCurve(self.convertFREDDatetoDate(date),
                                        marketId,
                                        lib1m[date],
                                        lib3m[date],
                                        lib6m[date],
                                        lib1y[date],
                                        lib2y[date],
                                        lib3y[date],
                                        lib4y[date],
                                        lib5y[date],
                                        lib7y[date],
                                        lib10y[date],
                                        lib30y[date])
      #      if counter > 5:
    #            break

def main():
#    fred.key('e732114c863993dcb376dac62f9e5473')
#    fredObservations = fred.observations('DSWP1')
#    observations = fredObservations['observations']
#    obs = observations['observation']
#    ob = obs[0]
#    for ob in obs:
#        print ob['date'] + '\t' + ob['value']
    loader = FREDLoader()
    print 'Processing EOD'
    loader.loadAllLiborCurves(marketId='EOD')
#    print values
if __name__ == "__main__":
    main()            