'''
Created on Oct 12, 2009

@author: capitalmarkettools
'''
class MarketDataMissing(Exception):
    def __init__(self, value=None):
        if value == None:
            value = "Some error that throws MarketDataMissing exception"
        super(MarketDataMissing, self).__init__(value)
    
class OtherException(Exception):
    def __init__(self, value=None):
        if value == None:
            value = "Some error that throws OtherException exception"
        super(OtherException, self).__init__(value)
        
class ParameterException(Exception):
    ''' Raise if a function parameter is incorrect '''
    def __init__(self, value=None):
        if value == None:
            value = "Some error that throws ParameterException exception"
        super(OtherException, self).__init__(value)

    
