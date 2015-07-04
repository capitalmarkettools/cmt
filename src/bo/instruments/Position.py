'''
Created on Oct 11, 2009

@author: capitalmarkettools
'''
from src.bo import cmt, ErrorHandling

class Position(cmt.cmt):
    '''
    Position is base class for equity and bond position"
    positionType can be 'Cash', 'Equity', 'Bond'
    '''
    def __init__(self, positionType='Cash', amount=1, secId='Cash'):
        cmt.cmt.__init__(self)
        self.positionType = positionType
        self.amount = amount
        self.secId = secId
        self.upToDate = False
        self.marketDataContainer = None
    
    def NPV(self, pricingDate):
        ''' does all the NPV calculations stand-alone '''
        raise ErrorHandling.OtherException()
    
    def marketData(self, pricingDate):
        ''' returns list of market data items '''
        raise ErrorHandling.OtherException()
        
    def loadAndSaveMarketData(self, pricingDate, marketId):
        ''' used to load market data from external source and saved it to DB '''
        raise ErrorHandling.OtherException()
        
    def setMarketDataContainer(self, marketDataContainer):
        self.marketDataContainer = marketDataContainer
        self.upToDate = False
    
    def getAssetType(self):
        raise ErrorHandling.OtherException()
            
    @classmethod
    def hasPositionType(self, positionType):
        if self.positionType == positionType:
            return True
        return False
    
def main():
    p = Position('Cash', 100, 'Cash')
    print p
if __name__ == "__main__":
    main()