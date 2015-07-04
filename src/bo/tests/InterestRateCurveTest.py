'''
Created on Sep 18, 2012

@author: Capital Market Tools
'''
import unittest
from src.models import InterestRate, InterestRateCurve
from src.bo.Enum import TimePeriod, Index
from src.bo.Date import Date
from src.bo import VARUtilities
from src.bo.static import Calendar
import QuantLib

class TestInterestRateCurve(unittest.TestCase):
    def setUp(self):
        self.pricingDate = Date(month=9,day=12,year=2011)
        QuantLib.Settings.instance().evaluationDate = self.pricingDate.ql()
    def tearDown(self):
        pass
    def testCreateCurveAndRates(self):
        curve = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                  numTerms=3, pricingDate=self.pricingDate)
        rate = InterestRate(term='M', numTerms=1, type='Deposit', mid=0.01,
                            curve=curve)
        curve.addRate(rate)
        cv = curve.buildZeroCurve()
        for node in cv.nodes():
            a = node
    def testSaveCurve(self):
        curve = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                  numTerms=3, pricingDate=self.pricingDate, marketId='TMP')
        rate = InterestRate(term='M', numTerms=1, type='Deposit', mid=0.01,
                            curve=curve)
        rate1 = InterestRate(term='M', numTerms=3, type='Deposit', mid=0.01,
                            curve=curve)
        curve.addRate(rate)
        curve.addRate(rate1)
        curve.save()
    def testLoadCurve(self):
        curve = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                  numTerms=3, pricingDate=self.pricingDate, marketId='TEST1')
        curve.load()
#        curve.printCurve()
    def testBuildMMCurve(self):
        curve = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                  numTerms=3, pricingDate=self.pricingDate, marketId='TEST1')
        curve.load()
#        curve.printCurve()
        cv = curve.buildZeroCurve()
        for node in cv.nodes():
            a = node
            
    def testBuildMMAndSwapFullCurve(self):
        curve = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                  numTerms=3, pricingDate=self.pricingDate)
        curve.addRate(InterestRate(term='M', numTerms=1, type='Deposit', 
                                   mid=0.003, curve=curve))
        curve.addRate(InterestRate(term='M', numTerms=3, type='Deposit', 
                                   mid=0.0039, curve=curve))
        curve.addRate(InterestRate(term='M', numTerms=6, type='Deposit', 
                                   mid=0.0056, curve=curve))
        curve.addRate(InterestRate(term='Y', numTerms=1, type='Swap', 
                                   mid=0.0052, curve=curve))
        curve.addRate(InterestRate(term='Y', numTerms=2, type='Swap', 
                                   mid=0.0054, curve=curve))
        curve.addRate(InterestRate(term='Y', numTerms=3, type='Swap', 
                                   mid=0.0066, curve=curve))
        curve.addRate(InterestRate(term='Y', numTerms=4, type='Swap', 
                                   mid=0.0089, curve=curve))
        curve.addRate(InterestRate(term='Y', numTerms=5, type='Swap', 
                                   mid=0.0116, curve=curve))
        curve.addRate(InterestRate(term='Y', numTerms=7, type='Swap', 
                                   mid=0.0164, curve=curve))
        curve.addRate(InterestRate(term='Y', numTerms=10, type='Swap', 
                                   mid=0.0214, curve=curve))
        curve.addRate(InterestRate(term='Y', numTerms=30, type='Swap', 
                                   mid=0.0295, curve=curve))

        cv = curve.buildZeroCurve()
        for node in cv.nodes():
            a = node
        
    def testBuild1RateCurve(self):
        curve = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                  numTerms=3, pricingDate=self.pricingDate, marketId='TEST1')
        rate = InterestRate(term='M', numTerms=1, type='Deposit', mid=0.01,
                            curve=curve)
        #TODO: Fix. this addRate adds the rate to the DB
        curve.addRate(rate)
        zeroCurve = curve.buildZeroCurve()
        for node in zeroCurve.nodes():
            a = node
            
    def testShiftCurve(self):
        curve = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                  numTerms=3, pricingDate=self.pricingDate, marketId='TEST1')
        curve.load()
        #curve.printCurve()
        cv1 = curve.buildZeroCurve()
        curve.shift(0.01)
        cv2 = curve.buildZeroCurve()
        for node in cv1.nodes():
            a = node
        for node in cv2.nodes():
            a = node
    def testUpdateRate(self):
        '''
        Tests the update of a rate value and save it to DB
        '''
        curve = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                  numTerms=3, pricingDate=self.pricingDate, marketId='TMP')
        curve.addRate(InterestRate(term='M', numTerms=1, type='Deposit', 
                                   mid=0.01, curve=curve))
        curve.addRate(InterestRate(term='M', numTerms=3, type='Deposit', 
                                   mid=0.01, curve=curve))        
        curve.save()
        curve = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                  numTerms=3, pricingDate=self.pricingDate, marketId='TMP')
        curve.load()
        self.failIf(curve.rates[1].mid <> 0.01, "Rate incorrect")
        self.failIf(len(curve.rates) <> 2, "Number of rates incorrect")
        curve.rates[1].mid = 0.02
        curve.save()
        curveAfterUpdate = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                             numTerms=3, pricingDate=self.pricingDate, marketId='TMP')
        curveAfterUpdate.load()
        self.failIf(curveAfterUpdate.rates[1].mid <> 0.02, "Updated rate incorrect")
        self.failIf(len(curveAfterUpdate.rates) <> 2, "Number of updated rates incorrect")
        curveAfterUpdate.rates[1].mid = 0.01
        curveAfterUpdate.save()
        curve = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                  numTerms=3, pricingDate=self.pricingDate, marketId='TMP')
        curve.load()
        self.failIf(curve.rates[1].mid <> 0.01, "Rate incorrect")
        self.failIf(len(curve.rates) <> 2, "Number of rates incorrect")
    def testSave2Curves(self):
        date = Date(month=9,day=13,year=2011)
        curve = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                  numTerms=3, pricingDate=date, marketId='TMP')
        rate = InterestRate(term='M', numTerms=1, type='Deposit', mid=0.01, curve=curve)
        curve.addRate(rate)
        curve.save()
        date1 = Date(month=9,day=14,year=2011)
        curve1 = InterestRateCurve(ccy='USD', index=Index('LIBOR'), term='M', 
                                   numTerms=3, pricingDate=date1, marketId='TMP')
        rate1 = InterestRate(term='M', numTerms=1, type='Deposit', mid=0.01)
        curve1.addRate(rate1)
        curve1.save()
        
#    def testBuildCurveOverManyDates(self):
#        timeSteps = VARUtilities.VARTimePeriodsAndSteps()
#        timeSteps.generate(start=Date(month=7,day=3,year=2000),
#                           end=Date(month=7,day=4,year=2000),
#                           num=10, term = TimePeriod('D'),
#                           calendar=Calendar.US())
#        for timeStep in timeSteps.timeSteps:
#            curve = InterestRateCurve(ccy='USD', index=Enum.Index('LIBOR'), term='M', 
#                                       numTerms=3, pricingDate=timeStep, marketId='EOD')
#            curve.load()
#            #curve.printCurve()
#            zeroCurve = curve.buildZeroCurve()
#            for node in zeroCurve.nodes():
#                a = node
                
    def testAddRate(self):
        
        pass
    #Load curve
    #add one rate
    #build curve
    #check zero rate that was added
    def testRemoveRate(self):
        pass
    #Load curve
    #remove one rate
    #build curve
    #check 2 zero rates around the item where it was removed    
def suite():
    return unittest.makeSuite(TestInterestRateCurve)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()