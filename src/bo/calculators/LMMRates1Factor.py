'''
Created on Sep 11, 2013

@author: Capital Market Tools
'''

class LMMRates1Factor(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.timeSteps=None
        self.path=None
        self.pricingDate=None
        self.timePeriods=None
        self.allPaths=None
        self.lmmVols=None
        self.swaptionVols=None
        self.curve=None
        
    def generatePaths(self):
        pass
    
    def price(self):
        pass
    
    