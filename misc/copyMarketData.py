'''
Created on Jul 21, 2013

@author: Capital Market Tools
'''

import datetime
from src.bo.Date import Date
from src.models import InterestRateCurve, InterestRate, StockPrice, BondOAS

class CopyMarketData(object):
    '''
    Copies all market data from some date and id to another date and id
    Overwrites everything
    '''
    
    def __init__(self, fromDate = None, toDate = None,
                 fromMarketId = None, toMarketId = None):
        self.copyRates(fromDate, toDate, fromMarketId, toMarketId)
        self.copyEquityPrices(fromDate, toDate, fromMarketId, toMarketId)
        self.copyBondOAS(fromDate, toDate, fromMarketId, toMarketId)
        
    def copyRates(self, fromDate, toDate, fromMarketId, toMarketId):
        curves = InterestRateCurve.objects.filter(pricingDate = fromDate, marketId = fromMarketId)
        for curve in curves:
            curve.loadRates()
            
            newCurve = InterestRateCurve(ccy=curve.ccy, index=curve.index, 
                                         term=curve.term, numTerms=curve.numTerms, 
                                         pricingDate=toDate, marketId=toMarketId)
            
            for rate in curve.getRates():
                newRate = InterestRate(type=rate.type, term=rate.term, numTerms=rate.numTerms, mid=rate.mid, curve=newCurve)
                newCurve.addRate(newRate)
            newCurve.save()

    def copyEquityPrices(self, fromDate, toDate, fromMarketId, toMarketId):
        prices = StockPrice.objects.filter(pricingDate=fromDate, marketId=fromMarketId)
        for price in prices:
            price.pk = None
            price.pricingDate = toDate
            price.marketId = toMarketId
            price.save()
             
    def copyBondOAS(self,  fromDate, toDate, fromMarketId, toMarketId):
        bondOASs = BondOAS.objects.filter(pricingDate = fromDate, marketId = fromMarketId)
        for bondOAS in bondOASs:
            bondOAS.pk = None
            bondOAS.pricingDate = toDate
            bondOAS.marketId = toMarketId
            bondOAS.save()
             
            
import sys
def main():
    print "Copying Start"
    if len(sys.argv) != 5:
        print "Needs 4 arguments: FromDate, FromMarketId, toDate, toMarketId"
        exit(-1)
    else:
        fromDate = Date()
        toDate = Date()
        fromDate.fromPythonDate(datetime.datetime.strptime(sys.argv[1],"%Y%m%d").date())
        toDate.fromPythonDate(datetime.datetime.strptime(sys.argv[3],"%Y%m%d").date())
        copier = CopyMarketData(fromDate = fromDate, 
                                fromMarketId = sys.argv[2],
                                toDate = toDate,
                                toMarketId = sys.argv[4])

    print "Copying Done"
if __name__ == "__main__":
    main()