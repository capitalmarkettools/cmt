'''
Created on Jul 24, 2013

@author: Capital Market Tools
'''

from src.models import Portfolio, ModelPosition, Transaction
from src.bo.Date import Date
from src.bo.instruments.FinancialInstrument import CreatePosition
from src.bo.MarketDataContainer import MarketDataContainer
from src.bo.Enum import PositionType, TransactionType
from src.bo.utilities.Converter import fToDC

class PerformanceCalculator(object):
    '''
    classdocs
    '''

    def __init__(self, start=None,end=None,portfolio=None,marketId=None):
        '''
        start, end, portfolio are required
        '''
        self.start = start
        self.end = end
        self.portfolio = portfolio
        self.marketId = marketId
        self.startValue = 0
        self.endValue = 0
        self.transactionValue = 0
        self.annualPerformance = 0
        self.periodPerformance = 0
        self.upToDate = False
        
    def calc(self):
#        print 'in calc'
        startDjangoPositions = ModelPosition.objects.filter(portfolio=self.portfolio, asOf=self.start)
        for djangoPosition in startDjangoPositions:
            position = CreatePosition(djangoPosition)
            self.portfolio.addPosition(position)
        marketDataContainer = MarketDataContainer()
        for position in self.portfolio.positions:
 #           print position
            marketDataContainer.add(position.marketData(pricingDate=self.start, marketId=self.marketId))
        for position in self.portfolio.positions:
            position.marketDataContainer = marketDataContainer
        self.startValue = self.portfolio.NPV(pricingDate=self.start,marketId=self.marketId)
  #      print 'Start value = %f' % self.startValue
        
        endPortfolio =Portfolio.objects.get(name=self.portfolio.name,user=self.portfolio.user)
        endDjangoPositions = ModelPosition.objects.filter(portfolio=endPortfolio, asOf=self.end)
        for djangoPosition in endDjangoPositions:
            position = CreatePosition(djangoPosition)
            endPortfolio.addPosition(position)
        marketDataContainer = MarketDataContainer()
        for position in endPortfolio.positions:
            marketDataContainer.add(position.marketData(pricingDate=self.end, marketId=self.marketId))
        for position in endPortfolio.positions:
            position.marketDataContainer = marketDataContainer
        self.endValue = endPortfolio.NPV(pricingDate=self.end,marketId=self.marketId)
   #     print 'End portfolio value = %f' % self.endValue

        #Adjust all positions but Cash ADD and REMOVE transactions so that I do not count them
        #We ignore the interest effect of these transactions
        transactions = Transaction.objects.filter(portfolio=endPortfolio,
                                                  transactionType = TransactionType('ADD'),
                                                  positionType = PositionType('CASH'),
                                                  ticker = 'Cash',
                                                  transactionDate__range=[self.start,self.end])

        #print transactions
        for transaction in transactions:
            self.transactionValue -= transaction.amount
            
        transactions = Transaction.objects.filter(portfolio=endPortfolio,
                                                  transactionType = TransactionType('REMOVE'),
                                                  positionType = PositionType('CASH'),
                                                  ticker = 'Cash',
                                                  transactionDate__range=[self.start,self.end])
        #print transactions
        for transaction in transactions:
            self.transactionValue += transaction.amount

        self.endValue += self.transactionValue
        #print 'Effective end value = %f' % self.endValue
        try:
            self.annualPerformance = ((self.endValue - self.startValue) / self.startValue) * \
                                    365.0 / (self.end.ql() - self.start.ql())   
        except ZeroDivisionError:
            self.annualPerformance = 0
        self.periodPerformance = self.annualPerformance * (self.end.ql() - self.start.ql()) / 365.0
        #print 'Annualized Performance is %f' % self.annualPerformance
        self.upToDate = True

    def report(self):
        if not self.upToDate:
            self.calc()
        msg = ''
        msg += 'Performance Report\n'
        msg += 'Portfolio=%s\n' % self.portfolio.name
        msg += 'Performance Period=[%s - %s]\n' % (self.start,self.end)
        msg += 'Start Value=%s\n' % fToDC(self.startValue)
        msg += 'End Value=%s\n' % fToDC(self.endValue)
        msg += 'Transaction Value=%s\n' % fToDC(self.transactionValue)
        msg += 'Period Performance=%.2f%%\n' % (self.periodPerformance*100.0) 
        msg += 'Annual Performance=%.2f%%\n' % (self.annualPerformance*100.0)
        return msg
            
def main():
    start = Date(month=8,day=30,year=2011)
    end = Date(month=9,day=12,year=2011)
    p = PerformanceCalculator(start=start,end=end,portfolio=Portfolio.objects.get(name='TEST1',user='TEST1'),marketId='TEST1')
    print p.report()

    for portfolio in Portfolio.objects.filter(user='benchmark'):
        try:
            p = PerformanceCalculator(start=Date(month=7,day=25,year=2013),
                                      end=Date(month=10,day=10,year=2013),
                                      portfolio=portfolio,marketId='EOD')
            p.calc()
            print p.portfolio.name + '\t' + '%.2f%%' % (p.periodPerformance*100.0) + '\t' + '%.2f%%' % (p.annualPerformance*100.0) 
        except:
            pass
if __name__ == "__main__":
    main()

