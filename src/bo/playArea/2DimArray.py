'''
Created on Oct 22, 2011

@author: Capital Market Tools
'''

from src.bo import Date

class Structure(object):
    '''
    IN PROGRESS
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.timePeriods = [] # vector of dates
        self.todaysMarketDataContainer = [] # vector of market data for today
        self.shifts = [] # vector of shifts between one day and the next
        self.scenarios = [] # vector of market data containers
        self.pnls = []
        self.returns = [] 
        
from scipy.interpolate import interp2d
def driver():
    #The logic below is used for interpolation of 
    #swaption volatility surface
    x = [1, 1, 3 , 3]
    y = [3, 5, 3, 5]
    z = [0.4, 0.5, 0.45, 0.55] 
    
    f = interp2d(x=x,y=y,z=z,kind='linear')
    
    print f(1, 3)
    print f(1, 5)
    print f(3, 3)
    print f(3, 5)
    print f(1,1)
    print f(0,0)
    print f(10,10)
    print f(2, 3)
    
def driver2():
    #test with single point
    x = [1, 1]
    y = [3, 5]
    z = [0.4, 0.5] 
    
    f = interp2d(x=x,y=y,z=z,kind='linear')
    
    print f(1, 3)
    print f(10,10)
    print f(2, 3)
    
if __name__ == "__main__":
    driver2()