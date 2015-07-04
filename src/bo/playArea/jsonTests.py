'''
Created on Sep 20, 2012

@author: Capital Market Tools
'''

from src.bo import Date
import json

class MyClass(object):
    '''
    classdocs
    '''
    def __init__(self):
        '''
        Constructor
        '''
    def encode(self):
        pass
    def decode(self):    
        pass
    
def main():
    #This does not work for Date. I will not use fixtures for now
    print 'Start'
    date = Date.Date(month=9,day=12,year=2011)
    date_string = json.dumps(date)
    print date_string
    newDate = json.load(date_string)
    print newDate
    print 'End'
    
if __name__ == "__main__":
    main()