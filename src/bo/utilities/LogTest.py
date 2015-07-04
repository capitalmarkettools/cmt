'''
Created on Oct 15, 2012

@author: Capital Market Tools
'''
import unittest
from src.bo.decorators import log

@log 
def nonClassFct1():
    pass
@log 
def nonClassFct2():
    pass
@log 
def nonClassFct3():
    nonClassFct2()

nonClassFct3()

class LogTest(unittest.TestCase):

    @log
    def fct1(self):
        pass
    @log
    def fct2(self, parm1, parm2):
        pass
    @log
    def fct3(self):
        self.fct1()
    @log
    def testCallLoggedFunctions(self):
        self.fct1()
        self.fct2(10,20)
        self.fct3()
        nonClassFct1()

def suite():
    return unittest.makeSuite(LogTest)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    