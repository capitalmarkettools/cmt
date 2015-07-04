'''
Created on Nov 14, 2009

@author: capitalmarkettools
'''
from src.bo import Date, ErrorHandling
from src.models import StockPrice, Equity

class MarketDataContainer(object):
    """Contains market data"""
    #TODO Add test cases
    def __init__(self):
        self.marketDataList = []
        
    def add(self, marketDataList):
        """Input: list of marketData"""
        for marketData in marketDataList:
            item = self.find(marketData)
            if item == None:
                self.marketDataList.append(marketData)
                
    def find(self, marketData):
        '''
        Input: marketData with keys filled
        Returns: marketData filled with data that's strored in 
        '''
        for item in self.marketDataList:
            #print marketData
            #print item
            if item.__class__.__name__ == marketData.__class__.__name__:
                #FIXME Implement compare operator
                if item.keysMatch(marketData):
                    return item
        return None 
    def create(self, portfolio, pricingDate, marketId):
        '''Creates the market data for the portfolio and date
        Input: portfolio, date
        '''
        for position in portfolio.positions:
            self.add(position.marketData(pricingDate=pricingDate, marketId=marketId))
#            
#    def __repr__(self):
#        return str(self)
#    
#    def __str__(self):
#        s = ""
#        for item in self.marketDataList:
#            s = s + str(item)
#        return s
    
def main():
    #create stockprice, add it to coainer and find it again
    pricingDate = Date.Date(month=9,day=12,year=2011)
    mContainer = MarketDataContainer()
    e = Equity()
    e.ticker = 'GOOG'
    s1 = StockPrice()
    s1.equity = e
    s1.pricingDate = pricingDate
    s1.marketId = ''
    s1.mid = 1.234
    l = []
    l.append(s1)
    mContainer.add(l)
    print mContainer
    print mContainer.find(s1)
    #create another one and fail to find it
    s2 = StockPrice()
    s2.equity = e
    s2.pricingDate = Date.Date(month=9,day=13,year=2011)
    s2.marketId = ''
    s2.mid = 1.234
    print mContainer.find(s2)

if __name__ == "__main__":
    main()