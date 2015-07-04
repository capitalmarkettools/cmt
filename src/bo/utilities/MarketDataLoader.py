'''
Created on Oct 30, 2009

@author: capitalmarkettools
'''
from src.bo import ystockquote, ErrorHandling, Date, VARUtilities, Enum 
from src.bo.static import Calendar
from src.models import StockPrice, Equity, InterestRateCurve, InterestRate
from src.bo.decorators import log

LoadStartDate = Date.Date(month=1,day=1,year=1986)
LoadEndDate = Date.Date(month=11,day=26,year=2011)

class EquityPriceLoader(object):
    '''Ad-hoc class that helps loading equity prices into DB
    '''
    def __init__(self):
        pass
    
    def loadHistoricalPricesFromYahoo(self, secId, fr, to, marketId):
        '''
        Downloads prices from yahoo for one secId over a time period
        '''
        quotes = ystockquote.get_historical_prices(secId, fr.str_yyyymmdd(), 
                                                   to.str_yyyymmdd())
        #print quotes
        if "Not Found" in str(quotes[1][0]):
            raise ErrorHandling.MarketDataMissing('%s with pricing date %s' % (secId, fr))
        for quote in quotes:
            #print quote
            if quote[0] == 'Date':
                continue
            year = int(quote[0][0:4])
            month = int(quote[0][5:7])
            day = int(quote[0][8:10])
            mid = float(quote[4])
            equities = Equity.objects.filter(ticker=secId)
            stockPrice = StockPrice()
            stockPrice.pricingDate = Date.Date(day,month,year)
            stockPrice.mid = mid
            stockPrice.equity = equities[0]
            stockPrice.marketId = marketId
            #print 'Saving %s ' % (stockPrice)
            stockPrice.save()
            
    def loadCurrentPriceFromYahoo(self, secId, today, marketId):
        '''
        Loads current price from yahoo and daves it as of today
        '''
        price = ystockquote.get_price(secId)
        try:
            if "Not Found" in price or float(price) < 0.000001:
                raise ErrorHandling.MarketDataMissing('Current price for %s is %s' % (secId,price))
        except:
            raise ErrorHandling.MarketDataMissing('price: %s is bad value' % price)
        mid = float(price)
        stockPrice = StockPrice()
        stockPrice.pricingDate = today
        stockPrice.mid = mid
        stockPrice.equity = Equity.objects.get(ticker=secId)
        stockPrice.marketId = marketId
        stockPrice.save()
    
    def loadStockPriceFromCSVFile(self, fileName):
        '''
        Downloads prices from fileName. fileName needs to include full path
        '''
        file = open(fileName,'r')
        for line in file:
            #print line
            items = line.split(',')
            #skip first line which is headers
            if items[0] == 'date':
                continue
            #print items
            date = items[0]
            ticker = items[1]
            mid = float(items[2])
            marketId = items[3]
            dateItems = date.split('/')
            month = int(dateItems[0])
            day = int(dateItems[1])
            year = int(dateItems[2])
            equities = Equity.objects.filter(ticker=ticker)
            if len(equities) <> 1:
                raise ErrorHandling.OtherException('error with ticker %s and return %s' % 
                                                       (ticker, equities))
            stockPrice = StockPrice()
            stockPrice.pricingDate = Date.Date(day=day,month=month,year=year)
            stockPrice.mid = mid
            stockPrice.marketId = marketId
            stockPrice.equity = equities[0]
#            print 'Saving %s ' % (stockPrice)
            stockPrice.save()
    
    def createDateFromString(self,date):
        dateItems = date.split('/')
        month = int(dateItems[0])
        day = int(dateItems[1])
        year = int(dateItems[2])
        return Date.Date(month=month,day=day,year=year)
    
    def loadInterestRateFromCSVFile(self, fileName):
        '''
        Downloads prices from fileName. fileName needs to include full path
        '''
        file = open(fileName,'r')
        lastDate = Date.Date(month=1,day=1,year=1972)
        for line in file:
            items = line.split(',')
            #skip first line which is headers
            if items[0] == 'date':
                continue
            #create new curve if date has changed
            curveDate = self.createDateFromString(items[0])
            if curveDate <> lastDate:
                newCurve = InterestRateCurve()
                newCurve.pricingDate = curveDate
                newCurve.ccy = items[1]
                newCurve.index = items[2]
                newCurve.marketId = items[3]
                newCurve.term = items[4]
                newCurve.numTerms = int(items[5])
                newCurve.save()
                newCurve.load()
                #Delete all rates in case the curve already existed
                rates = InterestRate.objects.filter(curve=newCurve)
                if rates:
                    rates.delete()
            curve = InterestRateCurve()
            curve.pricingDate = curveDate
            curve.ccy = items[1]
            curve.index = items[2]
            curve.marketId = items[3]
            curve.term = items[4]
            curve.numTerms = int(items[5])
            curve.load()
            rate = InterestRate()
            rate.curve = curve
            rate.type = items[6]
            rate.term = items[7]
            rate.numTerms = int(items[8])
            rate.mid = float(items[9])
            rate.save()
            lastDate = curveDate
    @log    
    def loadHistoricalPricesForAllTickers(self):
        allEquities = Equity.objects.all()
        tickers = [equity.ticker for equity in allEquities]
        for ticker in tickers:
            try:
                self.loadHistoricalPricesFromYahoo(ticker, LoadStartDate, LoadEndDate, 'TEST1')
            except:
                pass
    @log
    def loadAllDummyIRCurves(self):
        date = LoadStartDate
        while date <= LoadEndDate:
            self.loadDummyIRCurve(date)
            date.nextDay()
            
    @log    
    def loadDummyIRCurve(self, pricingDate):
        curve = InterestRateCurve()
        curve.ccy = 'USD'
        curve.index = Enum.Index('LIBOR')
        curve.term = 'M'
        curve.numTerms = 3
        curve.pricingDate = pricingDate
        curve.marketId = 'TEST1'
        r1 = InterestRate()
        r1.type = 'Deposit'
        r1.term = 'M'
        r1.numTerms = 1
        r1.mid = 0.01
        r1.curve = curve
        r2 = InterestRate()
        r2.type = 'Deposit'
        r2.term = 'M'
        r2.numTerms = 3
        r2.mid = 0.01
        r2.curve = curve
        r3 = InterestRate()
        r3.type = 'Swap'
        r3.term = 'Y'
        r3.numTerms = 1
        r3.mid = 0.01
        r3.curve = curve
        r4 = InterestRate()
        r4.type = 'Swap'
        r4.term = 'Y'
        r4.numTerms = 5
        r4.mid = 0.01
        r4.curve = curve
        r5 = InterestRate()
        r5.type = 'Swap'
        r5.term = 'Y'
        r5.numTerms = 10
        r5.mid = 0.01
        r5.curve = curve
        r6 = InterestRate()
        r6.type = 'Swap'
        r6.term = 'Y'
        r6.numTerms = 30
        r6.mid = 0.01
        r6.curve = curve
        curve.addRate(r1)
        curve.addRate(r2)
        curve.addRate(r3)
        curve.addRate(r4)
        curve.addRate(r5)
        curve.addRate(r6)
        curve.save()

def loadTickers():
    """Loads some hardcoded ticker prices from 1986 to 2009"""
    tickers = ['ALU','C','CMCSA','CSCO','GE','HD','IBM','INTC','JNJ','LSI','MRK','MSFT',
               'PFE','T','TWX','VZ','WMT', 'GOOG', 'MSY', 'IBM', 'GS']
    
    loader = EquityPriceLoader()
    for ticker in tickers:
        print 'Processing %s' % ticker
        equities = Equity.objects.filter(ticker=ticker)
        if not equities:
            equity = Equity()
            equity.ticker = ticker
            equity.save()
        loader.loadHistoricalPricesFromYahoo(ticker, LoadStartDate, LoadEndDate)

def loadNYSETickers():
    source = open('C:/Home/eclipse/workspace/VAR/data/NYSETickers.txt', 'r')
    loader = EquityPriceLoader()
    counter = 0
    for line in source:
        counter += 1
        #skip first 2 lines
        if counter < 3:
            continue
        items = line.split(',')
        ticker = items[1].strip('\"')
        print 'processing %s' % ticker
        try:
            equities = Equity.objects.filter(ticker=ticker)
            if not equities:
                equity = Equity()
                equity.ticker = ticker
                equity.save()
            loader.loadHistoricalPricesFromYahoo(ticker, LoadStartDate, LoadEndDate)
        except ErrorHandling.MarketDataMissing, e:
            print 'Error %s for %s' % (e,ticker)
            continue
        
def loadIRCurves():
    timePeriods = VARUtilities.VARTimePeriodsAndSteps()
    timePeriods.generate(LoadStartDate, LoadEndDate, 1, 
                       Enum.TimePeriod('D').ql(), Calendar.Target())
    for time in timePeriods.timeSteps:
        print time
        curve = InterestRateCurve()
        curve.loadDefault(time)
        curve.save()

def createInitialMarketDataPopulation():
    loadTickers()
    loadIRCurves()
    
def deleteMarketDataPopulation():
    print "pass"
    print "please delete tables manually"
    pass

def main():
#    loadHestonMarketData()
#    loadTickers()
#    createInitialMarketDataPopulation()
    loader = EquityPriceLoader()
#    loader.loadHistoricalPricesForAllTickers()
#    loader.loadAllDummyIRCurves()
#    loader.loadStockPriceFromCSVFile('C:/Home/eclipse/cmt/misc/data/StockPricesForTEST11986-2011.csv')
#    loader.loadStockPriceFromCSVFile('C:/Home/eclipse/cmt/misc/data/StockPricesForHVaRTests.csv')
#    loader.loadInterestRateFromCSVFile('C:/Home/eclipse/cmt/misc/data/InterestRatesForHVaRTests.csv')
#    loader.loadStockPriceFromCSVFile('C:/Home/eclipse/cmt/misc/data/equityStockPricesLargeSet.csv')
    loader.loadHistoricalPricesFromYahoo(secId='GOOG',fr=Date.Date(20,3,2012),to=Date.Date(20,3,2012),marketId='EOD')
#    loader.loadHistoricalPricesFromYahoo('IBM',Date.Date(20,3,2008),Date.Date(20,3,2012))
if __name__ == "__main__":
    main()
