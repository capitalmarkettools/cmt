'''
Created on Sep 11, 2013

@author: Capital Market Tools
'''

import numpy as np
from src.bo import ErrorHandling
import math, time


class LMMRates1Factor(object):
    '''
    classdocs
    '''

    def __init__(self, N=10, M=120, pricingDate=None):
        '''
        N is number of simulation paths
        M is number of timesteps and well as length of curve. Always assume 10 years
        Many values hardcoded with fairly realistic values
        '''
        N = 10000
        M = 30
        maturity = 10.0
#        if pricingDate == None:
 #           ErrorHandling.OtherException('PricingDate required')
        self.M=None
        self.pricingDate=pricingDate
        self.timePeriods=np.empty(M)
        self.timePeriods.fill(maturity/M)
        self.allPaths=np.zeros(shape=(N, M, M))
        self.lmmVols=np.empty(shape=(M,M))
        self.lmmVols.fill(0.4)
        self.swaptionVols=np.empty(shape=(M,M))
        self.swaptionVols.fill(0.45)
        self.curve=np.zeros(M)
        self.curve.fill(0.2)
        
    def generatePaths(self):
        '''
        Generates paths
        '''
        drift = 0.0
        #loop over simulation paths
        for s in xrange(self.allPaths.shape[0]):
            #Initialize first curve vector
            for ct in xrange(self.curve.shape[0]):
                self.allPaths[s, 0, ct] = self.curve[ct]
            #loop over forward time to set next timestep. we do not need to cover last t as we set next t always
            for t in xrange(self.allPaths.shape[1]-1):
                #code explicitly the change in the forward curves
                #we do not propagate all forward rates as we have a triangular matrix
                #the forward roll down
                #all the indices need to be double checked
                for ct in xrange(self.allPaths.shape[2]-1-t):
                    #self.allPaths[s,t+1,ct] = 9.9
                    f = self.allPaths[s,t,ct+1]
                    self.allPaths[s,t+1,ct] = f + f * drift * self.timePeriods[ct] + f * self.lmmVols[t,ct] * np.random.normal() * math.sqrt(self.timePeriods[ct])
        
    def price(self):
        '''
        Price discount bond in 2 years
        '''
 #       print self.allPaths.shape[0]
        prices = np.empty(self.allPaths.shape[0])
        prices.fill(1.0)
#        print prices
        for s in xrange(self.allPaths.shape[0]):
#            print 'Path ' + str(s)
            #go out 5 years
            for t in xrange(24):
                prices[s] = prices[s] / (1.0 + self.allPaths[s, t, 0] * self.timePeriods[0])
 #               print t, prices[s] 
        return prices.mean()
                
    def price_static(self):
        '''
        not expected to match as there is a drift
        '''
        price = 1.0
        for t in xrange(24):
            price = price / (1.0 + 0.2 * self.timePeriods[t])
        return price
    
if __name__ == "__main__":
    print 'Start'
    start = time.time()
    lmm = LMMRates1Factor()
#    print 'timePeriods:', lmm.timePeriods
#    print 'allPaths', lmm.allPaths
    lmm.generatePaths()
 #   print 'allPaths after generate', lmm.allPaths
    print 'MC Price ', lmm.price()
    print 'Static Price', lmm.price_static()
    print 'Error', lmm.price() - lmm.price_static()
    end = time.time()
    print 'Execution time in seconds ', end - start
    