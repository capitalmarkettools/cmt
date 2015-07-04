'''
Created on May 6, 2011

@author: Capital Market Tools
'''
from src.bo.instruments import EquityPosition, BondPosition
from src.bo.instruments import CashPosition, SwapPosition
from src.bo.Enum import PositionType
from src.bo import ErrorHandling, cmt

#def mapStringToPositionClassType(string):
#    if string == 'EquityPosition':
#        positionType = EquityPosition.EquityPosition().__class__
#    elif string == 'BondPosition':
#        positionType = BondPosition.BondPosition().__class__
#    else:
#        raise ErrorHandling.OtherException()
#    return positionType

#def CreatePosition(positionType):
#    for cls in Position.__subclasses__():
#        if cls.hasPositionType(positionType):
#            return cls(positionType)
#    raise ValueError
#def CreatePosition(object):
#    ''' generic function to create position instance
#    object requires posType and cP attributes
#    cp stands for constructor Parameters
#    '''
    #if object does not have the attr needed then throw exception
    #loop over all 
def CreatePosition(modelPosition):
    '''
    Note: Position does not have an as of date but Portfolio does
    '''
    #TODO Change Create Position to take models.Position as input and not three parameters
    if modelPosition.positionType == PositionType('EQUITY'):
        obj = EquityPosition.EquityPosition(amount=modelPosition.amount, secId=modelPosition.ticker)
    elif modelPosition.positionType == PositionType('BOND'):
        obj = BondPosition.BondPosition(amount=modelPosition.amount, secId=modelPosition.ticker)
    elif modelPosition.positionType == PositionType('CASH'):
        obj = CashPosition.CashPosition(amount=modelPosition.amount)
    elif modelPosition.positionType == PositionType('SWAP'):
        obj = SwapPosition.SwapPosition(amount=modelPosition.amount, secId=modelPosition.ticker)
    else:
        raise ErrorHandling.OtherException('Position Type %s not suppoerted'% str(modelPosition.positionType))
    return obj

class FinancialInstrument(cmt.cmt):
    '''
    Financial Instrument base class
    '''
    def __init__(self, instrumentName):
        self.instrumentName = instrumentName
    def hasInstrumentName(self, instrumentName):
        if self.instrumentName == instrumentName:
            return True
        return False
    
def CreateFinancialInstrument(instrumentName):
    for cls in FinancialInstrument.__subclasses__():
        if cls.hasInstrumentName(instrumentName):
            return cls(instrumentName)
    raise ValueError


def main():
    print 'Start'
    print 'Base class. Nothing to run'
    print 'End'     
if __name__ == "__main__":
    main()
