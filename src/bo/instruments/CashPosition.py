'''
Created on Feb 2, 2010

@author: capitalmarkettools
'''
from src.bo.instruments import Position
from src.bo.decorators import log
from src.bo.Enum import AssetType

@log
class CashPosition(Position.Position):
    """BondPosition consists of amount and secId"""
    def __init__(self, amount):
        Position.Position.__init__(self, positionType='Cash', amount=amount, secId='Cash')
        
    def __str__(self):
        return '<%s,%s>' % (self.__class__, self.amount)
    
    def marketData(self, pricingDate, marketId):
        return []
    
    def NPV(self, pricingDate, marketId):
        return float(self.amount)

    def getAssetType(self):
        return AssetType('CASH')

def main():
    pass
if __name__ == "__main__":
    main()