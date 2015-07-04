'''
Created on Feb 1, 2010

@author: capitalmarkettools
'''
import QuantLib
from src.bo import cmt, ErrorHandling

class Basis(cmt.cmt):
    choices=(('A360','Actual/360'),
             ('30360','30/360'),
             ('ACTACT','Actual/Actual'),)

    def __init__(self, basis=None):
        super(Basis, self).__init__()
        self._basis = basis
        
    def __eq__(self, value):
        #TODO: Not sure how to fix this
        if value is None:
            return False
        return True
    def __ne__(self, value):
        return not self == value
    
    #TODO: LOW: Remove hardcoding of 20 for length
    def __len__(self):
        return 8

    def DBString(self):
        return None
    
    def __str__(self):
        return self._basis

#    def set_value(self, value):
 #       self._basis = value
    
  #  def get_value(self):
   #     return self._basis
    
    #basis = property(get_value, set_value)
    
    def ql(self):
        return self
        
class Actual360(Basis):
    '''Inherited directly from QuantLib.Actual360
    '''
    def __init__(self):
        super(Actual360, self).__init__()
        self._basis = 'A360'
    def __eq__(self, value):
        #TODO: Not sure how to fix this
        if value is None:
            return False
        return True
    def __ne__(self, value):
        return not self == value

    def DBString(self):
        return 'A360'
    
    def ql(self):
        b = QuantLib.Actual360()
        return b
    
class Thirty360(Basis):
    '''Inherited directly from QuantLib.Thirty360
    '''
    def __init__(self):
        super(Thirty360, self).__init__()
        self._basis = '30360'
        
    def __eq__(self, value):
        #TODO: Not sure how to fix this
        if value is None:
            return False
        return True
    def __ne__(self, value):
        return not self == value

    def DBString(self):
        return '30360'

    def ql(self):
        b = QuantLib.Thirty360()
        return b

class ActualActual(Basis):
    '''Inherited directly from QuantLib.ActualActual
    '''
    def __init__(self):
        super(ActualActual, self).__init__()
        self._basis = 'ACTACT'

    def __eq__(self, value):
        #TODO: Not sure how to fix this
        if value is None:
            return False
        return True
    def __ne__(self, value):
        return not self == value

    def DBString(self):
        return 'ACTACT'
    
    def ql(self):
        b = QuantLib.ActualActual()
        return b
    
def createBasis(s):
    if s == '' or s == None:
        return None
    elif s == 'A360':
        return Actual360()
    elif s == '30360':
        return Thirty360()
    elif s == 'ACTACT':
        return ActualActual()
    else:
        raise ErrorHandling.OtherException('Basis cannot be created with %s' % s)
    
def main():
    print 'Start'
    basis1 = Actual360()
    basis2 = Thirty360()
    basis3 = createBasis('A360')
    
    print '%s\t%s\t%s' % (basis1, basis2, basis3)
    import json
    print json.dumps(basis1)
    print 'End'     
    
if __name__ == "__main__":
    main()