'''
Created on Oct 30, 2009

@author: capitalmarkettools
'''
from src.bo import ystockquote, ErrorHandling, Date, VARUtilities, Enum 
from src.bo.static import Calendar
from src.models import StockPrice, Equity, InterestRateCurve, InterestRate
from settings import ROOT_PATH

LoadStartDate = Date.Date(1,1,1986)
LoadEndDate = Date.Date(26,11,2011)
#LoadStartDate = Date.Date(month=9,day=12,year=2011)
#LoadEndDate = Date.Date(month=9,day=12,year=2011)

class EquityPriceTextFileCreator(object):
    '''
    Creates a text file with a large set of equity prices
    The text file will then be loaded in DBInitialData'''
    def __init__(self):
        self.fileName = ROOT_PATH+'/misc/data/equityStockPricesLargeSet.csv'
        self.tickers = ['ALU','C','CMCSA','CSCO','GE','HD','IBM','INTC','JNJ','LSI','MRK','MSFT',
                        'PFE','T','TWX','VZ','WMT', 'GOOG', 'MSY', 'IBM', 'GS']
#        self.tickers = ['ALU']
        self.marketId = 'TEST1'
        
    def priceFromYahoo(self, secId, date):
        '''
        Downloads prices from yahoo for one secId over a time period
        '''
#        print 'pre yahoo call for %s' % secId
        quotes = ystockquote.get_historical_prices(secId, date.str_yyyymmdd(), date.str_yyyymmdd())
#        print 'post yahoo call'
        #print quotes
        if len(quotes) <> 2:
            print 'bad quote for %s on %s' % (secId, str(date))
            return -1
            raise ErrorHandling.OtherException('quotes vector has 0 or more than 1 elements')
        if str(quotes[1][0]).find("Not Found") <> -1:
            raise ErrorHandling.MarketDataMissing("%s with pricing date %s" % (secId, date))
        for quote in quotes:
            #print quote
            if quote[0] == 'Date':
                continue
            mid = float(quote[4])
        print 'quote for %s on %s is %s' % (secId,str(date),str(mid))
        return mid
    
    def execute(self):
        f = open(self.fileName, 'w')
        date = LoadStartDate
        while date <= LoadEndDate: 
            for ticker in self.tickers:
                price = self.priceFromYahoo(secId=ticker, date=date)
                if price <> -1:
                    f.write(str(date)+','+ticker+','+str(price)+','+self.marketId+'\n')
            date.nextDay()
        f.close()
        
    def createDateFromString(self,date):
        dateItems = date.split('/')
        month = int(dateItems[0])
        day = int(dateItems[1])
        year = int(dateItems[2])
        return Date.Date(month=month,day=day,year=year)
    
def main():
#    loadHestonMarketData()
#    loadTickers()
#    createInitialMarketDataPopulation()
    creator = EquityPriceTextFileCreator()
    creator.execute()
if __name__ == "__main__":
    main()