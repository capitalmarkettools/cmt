'''
Created on May 6, 2011

@author: capitalmarkettools
'''
from src.bo.instruments import Position
from src.bo import ErrorHandling
from src.models import StockPrice, Equity
from src.bo.utilities.MarketDataLoader import EquityPriceLoader

class EquityPosition(Position.Position):
    "EquityPosition consists of amount and secId"
#TODO: Amend EquityPosition to use Equity underlying rather than secId string
    def __init__(self, amount, secId):
        Position.Position.__init__(self, 'EquityPosition', amount, secId)
        self.positionType = 'EquityPosition'
    def __str__(self):
        return '%s,%s,%s,%d' % (self.__class__,self.positionType,self.secId,self.amount)
#TODO Add __repr__ for debugging info about object
    def NPV(self, pricingDate=None, marketId=''):
        if pricingDate == None:
            raise ErrorHandling.ParameterException('pricingDate cannot be None')
        if self.marketDataContainer == None:
            raise ErrorHandling.MarketDataMissing('marketDataContainer is None')
        e = Equity()
        e.ticker = self.secId
        s = StockPrice()
        s.equity = e
        s.pricingDate = pricingDate
        s.marketId = marketId
        stockPrice = self.marketDataContainer.find(s)
        if stockPrice == None:
            msg = 'Cannot find market data %s in marketDataContainer' % s
            raise ErrorHandling.MarketDataMissing(msg)
        return float(self.amount) * stockPrice.mid
    def marketData(self, pricingDate=None, marketId=''):
        if pricingDate == None:
            raise ErrorHandling.ParameterException('pricingDate cannot be None') 
        qs = StockPrice.objects.filter(equity__ticker=self.secId, marketId=marketId, pricingDate=pricingDate)
        if not qs:
            msg = '%s on %s with marketId %s does not exist' % (self.secId, pricingDate, marketId)
            raise ErrorHandling.MarketDataMissing(msg)
        stockPrice = qs[0]
        l = []
        l.append(stockPrice)
        return l
    
    def loadAndSaveMarketData(self, pricingDate, marketId):
        '''
        Loads Price from Yahoo and stores it in the DB
        '''
        loader = EquityPriceLoader()
        loader.loadHistoricalPricesFromYahoo(secId=self.secId, fr=pricingDate, to=pricingDate, marketId=marketId)
        
    def getAssetType(self):
        equity = Equity.objects.get(ticker=self.secId)
        return equity.assetType

def main():
    e = EquityPosition(100, "GOOG")
    print str(e)
if __name__ == "__main__":
    main()   