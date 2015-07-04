'''
Created on Jan 26, 2013

@author: cmt
'''

def fToDC(floatValue):
        '''converts float to Currency Unit and Cents'''
        return '{:,.2f}'.format(floatValue)

def fToD(floatValue):
        '''converts float to Currency Unit and Cents'''
        return '{:,.0f}'.format(floatValue)
#        return str("$%.0f" % "{:,}".format(floatValue))
    
#    "{:,}".format(value)

def uniqueList(seq):
    newList = []
    for s in seq:
        if s not in newList:
            newList.append(s)
    return newList