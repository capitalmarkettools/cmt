'''
Created on Sep 30, 2013

@author: Capital Market Tools
'''
from src.bo import ErrorHandling
from src.bo.cmt import cmt
import json

class Calculator(cmt):
    '''
    Calculator Report base class
    '''
    def __init__(self, parameters = None):
        '''
        Constructor
        '''
#        print parameters
        if parameters == None:
            raise ErrorHandling.OtherException('parameters must be passed')
        if not isinstance(parameters, CalculatorParameters):
            raise ErrorHandling.OtherException('CalculatorParameters class must be passed as parameters')
        self._results = []
        self._upToDate = True
        self._parameters = parameters
    
    def calc(self):
        pass
    
    def report(self):
        '''
        Must return jsan object
        '''
        if not self._upToDate:
            self.calc()
        ret = []
        for result in self._results:
            row = []
            for item in result:
                row.append(str(item))
            ret.append(row)
        return json.dumps(ret)
    
    def prettyPrint(self):
        ret = ''
        for result in self._results:
            for item in result:
                ret += str(item) + '\t'
            ret += '\n'
        return ret
    
    def results(self):
        return self._results
    
class CalculatorParameters(cmt):
    '''
    Calculator Report Input class
    This class is parallel to all Calculator classes
    Parameters will be passed
    '''

    def __init__(self):
        '''
        Constructor
        '''
        pass
