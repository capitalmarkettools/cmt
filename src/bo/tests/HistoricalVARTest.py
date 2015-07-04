'''
Created on Oct 26, 2009

@author: capitalmarkettools
'''
import unittest
import QuantLib
import math
from scipy.stats.stats import pearsonr, moment
from src.bo.instruments import EquityPosition
from src.bo import HistoricalVAR, Enum
from src.bo import VARUtilities, Date, ErrorHandling
from src.bo.static import Calendar
from src.bo import MarketDataContainer
from src.bo.instruments import BondPosition
from src.bo.instruments.FinancialInstrument import CreatePosition
from src.models import Portfolio, ModelPosition
from src.bo.Enum import PositionType
    
class HVaRTest(unittest.TestCase):
    
    def setUp(self):
        self.pricingDate = Date.Date(month=9,day=12,year=2011)
        self.marketId = 'TEST1'
    #    self.tCBond = TCBond.objects.get(name='TEST1')

    def testOneEquityOver10Days(self):
        portfolio = Portfolio()
        position = EquityPosition.EquityPosition(100,'TEST1')
        portfolio.addPosition(position)
        pricingDate = self.pricingDate
        QuantLib.Settings.instance().evaluationDate = pricingDate.ql()
        timePeriods = VARUtilities.VARTimePeriodsAndSteps()
        timePeriods.generate(start = Date.Date(month=8,day=30,year=2011),
                             end = self.pricingDate,
                             num = 1, term = Enum.TimePeriod('D'), 
                             calendar = Calendar.US())
        analysis = HistoricalVAR.HistoricalVAR(pricingDate=pricingDate, 
                                                   portfolio=portfolio, 
                                                   timeSteps=timePeriods,
                                                   confidenceInterval=0.95,
                                                   marketId='TEST1')
     #   print '1: ' + str(analysis.run())
        #Ballpark test only. The value makes sense but not exactly reconciled
        self.failIf(abs(-0.0340637835262-analysis.run()) > 0.0000001, 
                    'Historical VaR result for TEST1 over 10 days incorrect')

    def testOneBondOver10Days(self):
        portfolio = Portfolio()
        position = BondPosition.BondPosition(100,'TEST1')
        portfolio.addPosition(position)
        pricingDate = self.pricingDate
        QuantLib.Settings.instance().evaluationDate = pricingDate.ql()
        timePeriods = VARUtilities.VARTimePeriodsAndSteps()
        timePeriods.generate(start = Date.Date(month=8,day=30,year=2011),
                             end = self.pricingDate,
                             num = 1, term = Enum.TimePeriod('D'), 
                             calendar = Calendar.US())
        analysis = HistoricalVAR.HistoricalVAR(pricingDate=pricingDate, 
                                                   portfolio=portfolio, 
                                                   timeSteps=timePeriods,
                                                   confidenceInterval=0.95,
                                                   marketId='TEST1')
      #  print '2: ' + str(analysis.run())
        #print analysis.pnlList
        #Ballpark test only. The value makes sense but not exactly reconciled
        self.failIf(abs(-0.0721904315632-analysis.run()) > 0.0000001, 
                    'Historical VaR result for TEST1 over 10 days incorrect')

    def testOneBondAndOneEquityOver10Days(self):
        portfolio = Portfolio()
        portfolio.addPosition(BondPosition.BondPosition(100,'TEST1'))
        portfolio.addPosition(EquityPosition.EquityPosition(100,'TEST1'))
        pricingDate = self.pricingDate
        QuantLib.Settings.instance().evaluationDate = pricingDate.ql()
        timePeriods = VARUtilities.VARTimePeriodsAndSteps()
        timePeriods.generate(start = Date.Date(month=8,day=30,year=2011),
                             end = self.pricingDate,
                             num = 1, term = Enum.TimePeriod('D'), 
                             calendar = Calendar.US())
        analysis = HistoricalVAR.HistoricalVAR(pricingDate=pricingDate, 
                                                   portfolio=portfolio, 
                                                   timeSteps=timePeriods,
                                                   confidenceInterval=0.95,
                                                   marketId='TEST1')
    #    print '3: ' + str(analysis.run())
        #Ballpark test only. The value makes sense but not exactly reconciled
        self.failIf(abs(-0.0510159444181-analysis.run()) > 0.0000001, 
                    'Historical VaR result for TEST1 over 10 days incorrect')
        
    def testTEST1PortfolioTEST1EquityCorrelation(self):
        pricingDate = self.pricingDate
        QuantLib.Settings.instance().evaluationDate = pricingDate.ql()
        portfolio1 = Portfolio.objects.get(name='TEST1', user='test1')
        modelPositions = portfolio1.modelposition_set.filter(asOf=pricingDate)
        for modelPosition in modelPositions:
            position = CreatePosition(modelPosition)
            portfolio1.addPosition(position)
#        for p in portfolio1.positions:
 #           print "************************************** %s" % str(p)

        timePeriods = VARUtilities.VARTimePeriodsAndSteps()
        timePeriods.generate(start = Date.Date(month=8,day=30,year=2011),
                             end = self.pricingDate,
                             num = 1, term = Enum.TimePeriod('D'), 
                             calendar = Calendar.US())
        analysis1 = HistoricalVAR.HistoricalVAR(pricingDate=pricingDate, 
                                                   portfolio=portfolio1, 
                                                   timeSteps=timePeriods,
                                                   confidenceInterval=0.95,
                                                   marketId='TEST1')
        analysis1.run()
        pnls1 = analysis1.getPnLList()
        portfolio2 = Portfolio()
        modelPosition = ModelPosition(portfolio=portfolio2,
                                      positionType=PositionType('EQUITY'),
                                      ticker='TEST1',
                                      amount=110,
                                      asOf=pricingDate)
        
        portfolio2.addPosition(CreatePosition(modelPosition))
        analysis2 = HistoricalVAR.HistoricalVAR(pricingDate=pricingDate, 
                                                   portfolio=portfolio2, 
                                                   timeSteps=timePeriods,
                                                   confidenceInterval=0.95,
                                                   marketId='TEST1')
        analysis2.run()
        pnls2 = analysis2.getPnLList()
#         print portfolio1.positions
#         print '********************************\n'
#         for p in portfolio1.positions:
#             print p
#         print '********************************\n'
#         print portfolio2.positions
#         for p in portfolio2.positions:
#             print p
#         print '********************************\n'
#        print pnls1
#        print pnls2
#        v1 = [pnl[1] for pnl in pnls1]
#        v2 = [pnl[1] for pnl in pnls2]
#        v1 = v1[1:]
#        v2 = v2[1:]
 #       print v1
  #      print v2
        pearsonCorr = pearsonr(pnls1,pnls2)
  #      print '3: ' + str(pearsonCorr[0])
        self.failIf(abs(0.655160228007 - pearsonCorr[0]) > 0.0000001, 
                    'Pearson Correlation for TEST1 portfolio vs TEST1 stock incorrect')
        
#These are old tests but that worked well before 
#all testing was changed to TEST1 stock and bond
    def createBondAndEquityPortfolio(self):
        portfolio = Portfolio()
        position = EquityPosition.EquityPosition(95,'TEST1')
        portfolio.addPosition(position)
        position = BondPosition.BondPosition(100,'TEST1')
        portfolio.addPosition(position)
        return portfolio
#    def test_GOOG_actual_pnl_2008_2009(self):
#        "Calculates worst day of actual P&L in 2008"
#        position = EquityPosition.EquityPosition(95,'GOOG')
#        portfolio = Portfolio()
#        portfolio.addPosition(position)
#        timeSteps = VARUtilities.VARTimePeriodsAndSteps()
#        timeSteps.generate(Date.Date(2,1,2008), Date.Date(31,12,2008), 1, Enum.TimePeriod('D'), Calendar.US())
#        pnlResults = []
#        prevTime = 0
#        marketDataContainer = MarketDataContainer.MarketDataContainer()
#        for time in timeSteps.timeSteps:
#            marketData = position.marketData(time)
#            marketDataContainer.add(marketData)
#        for p in portfolio.positions:
#            p.marketDataContainer = marketDataContainer
#        for time in timeSteps.timeSteps:
#            try:
#                npv = portfolio.NPV(time)
#            except ErrorHandling.MarketDataMissing:
#                npv = portfolio.NPV(prevTime)
##                logging.info("Price missing on %s. Used fallback from %s" % (time, prevTime))
#            pnlResults.append((time, npv))
#            prevTime = time
#        #Get max and min value
#        max = 0
#        min = 999999999999999999999
#        for result in pnlResults:
#            if result[1] > max:
#                max = result
#            elif result[1] < min:
#                min = result
#        #print "Max=%s/%f" % max
#        #print "Min=%s/%f" % min
#        self.failUnlessEqual(max[1], 65093.05, 'Error in max value')
#        self.failUnlessEqual(min[1], 28795.45, 'Error in min value')
#    def testEquityHVaR(self):
#        """Calculates HVAR for GOOG quaterly 
#        timesteps 2007/2008 with 95% conf.
#        """
#        pricingDate = Date.Date(16, 10, 2009)
#        portfolio = Portfolio()
#        portfolio.loadGoogle()
#        timePeriods = VARUtilities.VARTimePeriodsAndSteps()
#        timePeriods.generate_Q_20070301_20090203()
#        analysis = HistoricalVAR.HistoricalVAR(pricingDate, portfolio, 
#                                                   timePeriods, 0.95)
#        self.failIf(abs(-0.564838468136-analysis.run()) > 0.0000001, 
#                    'Historical VaR result for GOOG incorrect')
#    def test1YBondAndEquityActualPL(self):
#        pricingDate = Date.Date(16, 10, 2009)
#        QuantLib.Settings.instance().evaluationDate = pricingDate.ql()
#        portfolio = self.createBondAndEquityPortfolio()
#        timeSteps = VARUtilities.VARTimePeriodsAndSteps()
#        timeSteps.generate(Date.Date(2,1,2008), Date.Date(31,12,2008), 
#                           1, Enum.TimePeriod('D'), Calendar.US())
#        pnlResults = []
#        prevTime = 0
#        marketDataContainer = MarketDataContainer.MarketDataContainer()
#        for p in portfolio.positions:
#            for time in timeSteps.timeSteps:
#                marketData = p.marketData(time)
#                marketDataContainer.add(marketData)
#        for p in portfolio.positions:
#            p.marketDataContainer = marketDataContainer
#        for time in timeSteps.timeSteps:
#            #print "Pricing on " + str(time)
#            try:
#                npv = portfolio.NPV(time)
#            except ErrorHandling.MarketDataMissing:
#                npv = portfolio.NPV(prevTime)
#                #logging.info("Price missing on %s. Used fallback from %s" % (time, prevTime))
#            pnlResults.append((time, npv))
#            prevTime = time
#        #Get max and min value
#        max = 0
#        min = 999999999999999999999
#        for result in pnlResults:
#            if result[1] > max:
#                max = result
#            elif result[1] < min:
#                min = result
#        #print "Max=%s/%f" % max
#        #print "Min=%s/%f" % min
#        #self.failUnlessEqual(max[1], 65093.05, 'Error in max value')
#        #self.failUnlessEqual(min[1], 28795.45, 'Error in min value')
    def testBondAndEquityHVaR(self):
        pricingDate = self.pricingDate
        QuantLib.Settings.instance().evaluationDate = pricingDate.ql()
        portfolio = self.createBondAndEquityPortfolio()
        timeSteps = VARUtilities.VARTimePeriodsAndSteps()
        timeSteps.generate(Date.Date(month=8,day=30,year=2011), 
                           self.pricingDate, 
                           1, Enum.TimePeriod('D'), Calendar.US())
        hvar = HistoricalVAR.HistoricalVAR(pricingDate, portfolio, timeSteps, 0.99, 'TEST1')
   #     print "HVar = " + str(hvar.run())
        self.failIf(abs(-0.0700626431529-hvar.run()) > 0.0000001, 
                    'Historical VaR result for Bond plus Equity incorrect')
        
def suite():
    return unittest.makeSuite(HVaRTest)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_GOOG_95p']
    unittest.main()