'''
Created on Aug 29, 2013

@author: Capital Market Tools
'''
from src.models import TCBond, BondOAS
from src.bo.instruments.BondPosition import BondPosition
from src.bo.MarketDataContainer import MarketDataContainer
from src.bo.Date import Date
import numpy, math
from scipy.optimize import minimize

class ImplyOAS(object):
    '''
    classdocs
    '''

    def __init__(self, pricingDate=None,marketId=None,tCBond=None):
        '''
        All the data needs to be passed. Assume that pricingDate equals
        settlement date
        '''
        self.pricingDate = pricingDate
        self.marketId = marketId
        self.tCBond = tCBond
        self.price = 100.0
        
    def fct1(self,x):
#        print '__________________' + str(x)
        
        position = BondPosition(amount=1,tCBond=self.tCBond)
        marketDataContainer = MarketDataContainer()
        marketData = position.marketData(self.pricingDate, self.marketId)
#         #print marketData
        for m in marketData:
            if m.__class__ == BondOAS:
                m.mid = x[0]
        marketDataContainer.add(marketData)
        position.setMarketDataContainer(marketDataContainer)
        npv = position.NPV(self.pricingDate, self.marketId)
        result = math.fabs(npv-self.price)
#        print npv
 #       print self.price
        return result

    def implyOAS(self, price=100):
        self.price = price
        x0 = numpy.array([0.001])
        res = minimize(self.fct1, x0, method='nelder-mead',
                        options={'xtol': 1e-8, 'disp': False})
        return res.x[0]
    
if __name__ == '__main__':
    pass

            
def main():
    print 'Start'
    productionStartDate = Date(month=9,day=19,year=2013)
    implyOAS = ImplyOAS(tCBond=TCBond.objects.get(name='PortAuth_4.00_JAN42'),
                        marketId='EOD', pricingDate=productionStartDate)
    print implyOAS.implyOAS(price=87)
#     print implyOAS.implyOAS(price=95)
#     print implyOAS.implyOAS(price=96)
#     print implyOAS.implyOAS(price=97)
#     print implyOAS.implyOAS(price=98)
#     print implyOAS.implyOAS(price=99)
#     print implyOAS.implyOAS(price=100)
#     print implyOAS.implyOAS(price=101)
#     print implyOAS.implyOAS(price=102)
#     print implyOAS.implyOAS(price=103)
    print 'End'

if __name__ == "__main__":
    main()