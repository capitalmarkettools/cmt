'''
Created on Jul 24, 2013

@author: Capital Market Tools
'''

from src.bo.calculators.Calculator import Calculator, CalculatorParameters
from src.models import Portfolio, ModelPosition, Transaction
from src.bo.Date import Date
from src.bo.instruments.FinancialInstrument import CreatePosition
from src.bo.MarketDataContainer import MarketDataContainer
from src.bo.Enum import PositionType, TransactionType
from src.bo.utilities.Converter import fToDC

class PerformanceTickerCalculator(Calculator):
    '''
    classdocs
                raise ErrorHandling.OtherException('parameters must be passed')
        if not isinstance(parameters, CalculatorParameters):
            raise ErrorHandling.OtherException('CalculatorParameters class must be passed as parameters')
        self.results = []
        self.upToDate = True
        self.parameters = parameters
    '''
    

   def __init__(self, parameters = None):
        super(TimeSeriesNPVCalculator, self).__init__(parameters=parameters)
        self.startValue = 0
        self.endValue = 0
        self.annualPerformance = 0
        self.periodPerformance = 0
        
        
class ModelPosition(models.Model):
    portfolio = models.ForeignKey(Portfolio)
    positionType = modelFields.PositionTypeField(max_length=20)
    ticker = models.CharField(max_length=200, help_text='Equity, Bond or Swap identifier. Set Cash for cash')
    amount = models.FloatField()
    asOf = modelFields.DateField()
    
    def calc(self):
        
        modelPosition = ModelPosition(portfolio=None, positionType='EQUITY', ticker=self.parameters.ticker, amount=100,asOf=self.parameters.start)
        position = CreatePosition(modelPosition)
        marketDataContainer = MarketDataContainer()
        marketDataContainer.add(position.marketData(pricingDate=self.start, marketId=self.marketId))
        position.marketDataContainer = marketDataContainer
        self.startValue = startPortfolio.NPV(pricingDate=self.start,marketId=self.marketId)
        #print 'Start value = %f' % self.startValue
        self.endValue = endPortfolio.NPV(pricingDate=self.end,marketId=self.marketId)
        #print 'End portfolio value = %f' % self.endValue
        try:
            self.annualPerformance = ((self.endValue - self.startValue) / self.startValue) * \
                                    365.0 / (self.end.ql() - self.start.ql())   
        except ZeroDivisionError:
            self.annualPerformance = 0
        self.periodPerformance = self.annualPerformance * (self.end.ql() - self.start.ql()) / 365.0
        #print 'Annualized Performance is %f' % self.annualPerformance
        self.results.append((self.parameters.ticker, self.startValue, self.endValue, self.periodPerformance, self.annualPerformance))
        self.upToDate = True
            
class PerformanceTickerCalculatorParameters(CalculatorParameters):
    def __init__(self, start=None, end=None, ticker=None, marketId=None):
            self.start = start
            self.end = end
            self.marketId = marketId
            self.ticker = None


def main():
    start = Date(month=8,day=30,year=2011)
    end = Date(month=9,day=12,year=2011)
    p = PerformanceCalculatorTicker(start=start,end=end,portfolioName='TEST1',marketId='TEST1')
    print p.report()
    
if __name__ == "__main__":
    main()

