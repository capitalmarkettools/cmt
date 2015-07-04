'''9
Created on Jul 21, 2013

@author: Capital Market Tools
'''

import os 
import datetime
import settings
from collections import OrderedDict
from django.db.models import Q, Max
from django.core.mail import send_mail
from src.bo.Date import Date
from src.bo.utilities.Converter import fToDC, fToD
from src.models import Location, Equity, Transaction, ModelPosition,Portfolio, Batch
from src.models import InterestRateCurve, InterestRate, Allocation, StockPrice, BondOAS
from src.models import TCBond
from src.bo.Enum import Index, TimePeriod, Currency, AssetType
from src.bo.utilities.MarketDataLoader import EquityPriceLoader
from src.bo.ErrorHandling import MarketDataMissing
from src.bo.calculators.PerformanceCalculator import PerformanceCalculator
from src.bo.instruments.FinancialInstrument import CreatePosition
from src.bo.MarketDataContainer import MarketDataContainer
import QuantLib

class BatchUtility(object):
    '''
    Daily Batch that should be executed in windows scheduler
    '''

    
    def __init__(self, batchDate = None):
        '''
        Constructor
        '''
        self.productionStartDate = Date(day=25,month=7,year=2013)
        self.logFile = settings.BATCH_LOGS + 'batchLog.txt' 
        self.perfFile = settings.BATCH_LOGS + 'perf.txt'
        self.mtmFile = settings.BATCH_LOGS + 'mtm.txt'
        self.allocationFile = settings.BATCH_LOGS + 'allocation.txt'
		#Specify your email address to get notifications sent to
        self.email = 'XXX'
        self.marketId = 'EOD'
        self.maxBatchDate = Date()
        queryResult = Batch.objects.all().aggregate(Max('batchDate'))
        self.maxBatchDate.fromPythonDate(queryResult['batchDate__max'])
        if batchDate == None:
            today = datetime.date.today()
            self.batchDate = Date(month=today.month, day=today.day, year=today.year)
        else:
            self.batchDate = batchDate
            
        #prepare the batch so that we can save it if the batch finishes succesfully
        self.batch = Batch()
        self.batch.batchDate = self.batchDate
        
        print 'Running batch as of %s' % self.batchDate
        
    def run(self):
        #Log
        if os.path.isfile(self.logFile):
            os.remove(self.logFile)
        logFileHandle = open(self.logFile,'w')
        logFileHandle.write('Running batch as of %s\n' % self.batchDate)
        logFileHandle.write('Max batch is %s\n' % self.maxBatchDate)
#        if QuantLib.TARGET().isBusinessDay(self.batchDate.ql()) == False:
 #           logFileHandle.write('Not a good business date based on QuantLib TARGET calendar. Exiting ...')
  #          print('Not a good business date based on QuantLib TARGET calendar. Exiting ...')
        
        #Update locations with date
        logFileHandle.write('\nUpdating all locations except TEST1 with new date\n')
        locations = Location.objects.filter(~Q(name='TEST1'))
        for location in locations:
            logFileHandle.write('Updating location %s\n' % location.name)
            location.pricingDate = self.batchDate.toPythonDate()
            location.save()
        
        #Load Equity prices
        logFileHandle.write('\nLoading equity prices\n')
        equities = Equity.objects.all()
        equityLoader = EquityPriceLoader()
        for equity in equities:
            #skip TEST1 and TEST2 as they are only used for testing
            if equity.ticker in ['TEST1', 'TEST2']:
                continue
            if StockPrice.objects.filter(equity=equity, pricingDate=self.batchDate, marketId=self.marketId).exists() == True:
                logFileHandle.write('%s price exists\n' % equity.ticker)
                continue
            else:
                logFileHandle.write('Loading prices for equity %s\n' % equity.ticker)
                try:
                    equityLoader.loadCurrentPriceFromYahoo(secId=equity.ticker, 
                                                           today=self.batchDate,
                                                           marketId=self.marketId)
                except MarketDataMissing:
                    logFileHandle.write('No market data loaded for %s as of %s\n' % (equity.ticker, self.batchDate))
                    logFileHandle.write('As default loading price from last batch date\n')
                    lastPrice = StockPrice.objects.get(equity=equity, pricingDate=self.maxBatchDate, marketId=self.marketId)
                    lastPrice.pricingDate = self.batchDate
                    lastPrice.pk = None
                    lastPrice.save()
                   
        #Load Interest Rates        
        logFileHandle.write('\nLoading Interest Rates\n')
        if self.maxBatchDate != self.batchDate:
            logFileHandle.write('For now just copy rates from max batch date to current batch date\n')
            curve = InterestRateCurve.objects.get(ccy=Currency('USD'), index=Index('LIBOR'), 
                                                  term=TimePeriod('M'), numTerms=3, 
                                                  pricingDate=self.maxBatchDate, 
                                                  marketId='EOD')
            curve.loadRates()
            
            newCurve = InterestRateCurve(ccy=Currency('USD'), index=Index('LIBOR'), 
                                         term=TimePeriod('M'), numTerms=3, 
                                         pricingDate=self.batchDate, 
                                         marketId='EOD')
            
            for rate in curve.getRates():
                newRate = InterestRate(type=rate.type, term=rate.term, numTerms=rate.numTerms, mid=rate.mid, curve=newCurve)
                logFileHandle.write('Rate: %s/%d/%0.2f\n' % (rate.term, rate.numTerms, rate.mid*100))
                newCurve.addRate(newRate)
            newCurve.save()

        #Copy OAS forward and keep constant
        logFileHandle.write('\nCopying OAS from max batch date to batch date\n')
        if self.maxBatchDate != self.batchDate:
            bondOAS = BondOAS.objects.get(tCBond=TCBond.objects.get(name='PortAuth_4.00_JAN42'),
                                          marketId='EOD', pricingDate=self.maxBatchDate)
            bondOAS.pk = None
            bondOAS.pricingDate = self.batchDate
            bondOAS.save()
            
        #Process Positions
        logFileHandle.write('\nProcessing positions\n')
        #load all positions with the max date
        #if the batchDate greater than maxbatchdate then copy position to batchdate (roll position forward)
        if self.maxBatchDate < self.batchDate:
            positions = ModelPosition.objects.filter(asOf=self.maxBatchDate)
            for position in positions:
                logFileHandle.write('Copying position %s from max batch date to batch date\n' % position)
                position.pk = None
                position.asOf = self.batchDate
                position.save()

        #Update Positions based on Transactions
        logFileHandle.write('\nUpdating of positions based on transaction\n')
        transactions = Transaction.objects.filter(reflectedInPosition=False)
        if len(transactions) == 0:
            logFileHandle.write('No transactions to process\n')
        else:
            for transaction in transactions:
                logFileHandle.write('Processing transaction %s\n' % str(transaction))
                positions = transaction.relatedPositions()
                for position in positions:
                    logFileHandle.write('Processing position %s\n' % str(transaction))
                    transaction.updatePositionAmount(position=position)  
                    position.save() 
                transaction.reflectedInPosition = 'True'
                transaction.save()                 
            
        #Performance
        logFileHandle.write('\nRunning Performance Report\n')
        if os.path.isfile(self.perfFile):
            os.remove(self.perfFile)
        perfFileHandle = open(self.perfFile,'w')
        portfolios = Portfolio.objects.filter(user='cmt')
        startValue = 0
        endValue = 0
        for portfolio in portfolios:
            performanceCalculator = PerformanceCalculator(start=self.productionStartDate,
                                                          end=self.batchDate,
                                                          portfolio=portfolio,
                                                          marketId=self.marketId)
            perfFileHandle.write(performanceCalculator.report()+'\n')
            startValue += performanceCalculator.startValue
            endValue += performanceCalculator.endValue
            endValue += performanceCalculator.transactionValue
        
        if startValue == 0 or (self.batchDate.ql() - self.productionStartDate.ql()) == 0:
            overallPerformance = 0
        else:
            overallPerformance = ((endValue - startValue) / startValue) * 365.0 / (self.batchDate.ql() - self.productionStartDate.ql())
        perfFileHandle.write('Overall Period Performance = %.2f%%\n' % (overallPerformance*100.0/365.0*(self.batchDate.ql() - self.productionStartDate.ql())))
        perfFileHandle.write('Overall Annual Performance = %.2f%%' % (overallPerformance*100.0))
        perfFileHandle.close()
        
        #MTM and Positions
        logFileHandle.write('\nRunning MTM and Positions Report\n')
        totalValue = 0
        if os.path.isfile(self.mtmFile):
            os.remove(self.mtmFile)
        mtmFileHandle = open(self.mtmFile,'w')
        portfolios =Portfolio.objects.filter(user='cmt')
        mtmFileHandle.write('MTM Report as of %s\n' % self.batchDate)
        for portfolio in portfolios:
            mtmFileHandle.write('Portfolio=%s\n' % portfolio.name)
            modelPositions = ModelPosition.objects.filter(portfolio=portfolio, asOf=self.batchDate)
            for modelPosition in modelPositions:
                position = CreatePosition(modelPosition=modelPosition)
                portfolio.addPosition(position)
            marketDataContainer = MarketDataContainer()
            for position in portfolio.positions:
                marketDataContainer.add(position.marketData(pricingDate=self.batchDate, marketId=self.marketId))
            for position in portfolio.positions:
                position.marketDataContainer = marketDataContainer
            for position in portfolio.positions:
                positionValue = position.NPV(pricingDate=self.batchDate,marketId=self.marketId)
                mtmFileHandle.write('ModelPosition=%s with %.0f shares, asset type %s and value $%s\n' % (position.secId,
                                                                                                   position.amount,
                                                                                                   position.getAssetType(),
                                                                                                   fToDC(positionValue)))
            portfolioValue = portfolio.NPV(pricingDate=self.batchDate,marketId=self.marketId)
            mtmFileHandle.write('Portfolio value=$%s\n\n' % fToDC(portfolioValue))
            totalValue += portfolioValue
        mtmFileHandle.write('Total value=%s\n\n' % fToDC(totalValue))

        #Asset Allocation
        #allocations is associative array with value
        allocations = {}
        totalValue = 0
        for item in AssetType.choices:
            allocations[item[0]] = 0
        logFileHandle.write('\nRunning Allocation Report\n\n')
        if os.path.isfile(self.allocationFile):
            os.remove(self.allocationFile)
        allocationFileHandle = open(self.allocationFile,'w')
        portfolios =Portfolio.objects.filter(user='cmt')
        allocationFileHandle.write('Allocation Report as of %s\n\n' % self.batchDate)
        for portfolio in portfolios:
            if portfolio.name == 'TradeAug2013':
                continue
            modelPositions = ModelPosition.objects.filter(portfolio=portfolio, asOf=self.batchDate)
            for modelPosition in modelPositions:
                position = CreatePosition(modelPosition)
                portfolio.addPosition(position)
            marketDataContainer = MarketDataContainer()
            for position in portfolio.positions:
                marketDataContainer.add(position.marketData(pricingDate=self.batchDate, marketId=self.marketId))
            for position in portfolio.positions:
                position.marketDataContainer = marketDataContainer
            for position in portfolio.positions:
                npv = position.NPV(pricingDate=self.batchDate, marketId=self.marketId)
                allocations[str(position.getAssetType())] += npv
                totalValue += npv
        
        orderedAllocations = OrderedDict(sorted(allocations.items(),key=lambda t: t[1],reverse=True))
        for key in orderedAllocations.keys():
            try:
                allocationPercent = Allocation.objects.get(assetType=AssetType(key)).percent
            except:
                allocationPercent = 0.0
            try:
                actualAllocation = 100*orderedAllocations[key]/totalValue
            except:
                actualAllocation = 0.0
            allocationFileHandle.write('%s=%.0f%%\t\t\t\t\t\twith target %.0f%%\t and value $%s\n' % (key,
                                                                                           actualAllocation,
                                                                                           100*allocationPercent,
                                                                                           fToD(orderedAllocations[key])))
        
        logFileHandle.write('Batch completed\n')
        logFileHandle.close()
        
        #Every time I run the batch and it succeeds we need to save the batch info
        self.batch.save()
        
        
    def sendEmail(self):
        print "Sending email"
        mtmFileHandle = open(self.mtmFile,'r')
        send_mail('CMT MTM and Positions as of %s' % self.batchDate, mtmFileHandle.read(), self.email,[self.email], fail_silently=False)
        mtmFileHandle.close()

        perfFileHandle = open(self.perfFile,'r')
        send_mail('CMT Performance as of %s' % self.batchDate, perfFileHandle.read(), self.email,[self.email], fail_silently=False)
        perfFileHandle.close()
        
        allocationFileHandle = open(self.allocationFile,'r')
        send_mail('CMT Allocations as of %s' % self.batchDate, allocationFileHandle.read(), self.email,[self.email], fail_silently=False)
        allocationFileHandle.close()
        
        logFileHandle = open(self.logFile,'r')
        send_mail('CMT Log as of %s' % self.batchDate, logFileHandle.read(), self.email,[self.email], fail_silently=False)
        logFileHandle.close()
        
        
import sys
import datetime
def main():
    if len(sys.argv) == 1:
        batch = BatchUtility()
        batch.run()
        batch.sendEmail()
    else:
        for dateString in sys.argv[1:]:
            batchDate = Date()
            batchDate.fromPythonDate(datetime.datetime.strptime(dateString,"%Y%m%d").date())
            batch = BatchUtility(batchDate=batchDate)
            batch.run()
            batch.sendEmail()

#Sample of hardcoding a specific date
#    batchDate = Date(month=8,day=2,year=2013)
#    batch = BatchUtility(batchDate=batchDate)
#    batch = BatchUtility()
#    batch.run()
#    batch.sendEmail()

#Sample of catching up between dates
#    batchDate = Date(month=7,day=14,year=2014)
#    while batchDate < Date(month=1,day=25,year=2015):
#        batchDate.nextDay()
#        print 'Running batch as of ', batchDate
#        batch = BatchUtility(batchDate=batchDate)
#        batch.run()


#    batchDate = Date(month=8,day=2,year=2013)
#    batch = BatchUtility(batchDate=batchDate)
#    batch = BatchUtility()
#    batch.run()
#    batch.sendEmail()
    
    print "Batch done"
if __name__ == "__main__":
    main()
