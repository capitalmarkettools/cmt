'''
Created on Nov 12, 2009

@author: capitalmarkettools
'''
class MarketDataScenario(object):
    """Scenario of market data
    Has an issue with copy.deepcopy. When doing copy of scenario
    do deepcopy on the underlying market data
    """

    def __init__(self):
        self.name = None
        self.marketData = None
#    def __str__(self):
 #       return 'Name=%s\nMarketData=%s' % (self.name, self.marketData)
    def __repr__(self):
        return '<%s: %s/%s>' % (self.__class__.__name__, self.name, self.marketData) 

def main():
    pass
    
if __name__ == "__main__":
    main()          