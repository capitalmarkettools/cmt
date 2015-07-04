'''
Created on Jul 24, 2013

@author: Capital Market Tools
'''
import datetime
from src.bo.calculators.Calculator import Calculator, CalculatorParameters
from src.models import Batch, ModelPosition, Portfolio
from src.bo.Date import Date
from src.bo.instruments.FinancialInstrument import CreatePosition
from src.bo.MarketDataContainer import MarketDataContainer
from src.bo.ErrorHandling import OtherException
from src.bo.utilities import Converter
from src.bo import VARUtilities, Enum
from src.bo.static import Calendar
import copy

class TimeSeriesNPVCalculator(Calculator):
    def __init__(self, parameters = None):
        super(TimeSeriesNPVCalculator, self).__init__(parameters=parameters)

    def _value(self, portfolio=None, asOf=None):
        '''
        Values a portfolio as of asOf date
        Not sure why this is local to this class and not a portfolio parameter or a valuation class
        '''
        if portfolio==None or asOf==None:
            raise OtherException('portfolio and asOf must be passed')
        portfolio.positions = []
        modelPositions = ModelPosition.objects.filter(portfolio=portfolio, asOf=asOf)
        for modelPosition in modelPositions:
            position = CreatePosition(modelPosition)
            portfolio.addPosition(position)
        marketDataContainer = MarketDataContainer()
        for position in portfolio.positions:
            marketDataContainer.add(position.marketData(pricingDate=asOf, marketId=self._parameters.marketId))
        for position in portfolio.positions:
            position.marketDataContainer = marketDataContainer
        return portfolio.NPV(pricingDate=asOf,marketId=self._parameters.marketId)

    def calc(self):
        '''
        We'll keep it simple. We load all positions for each date and just value it
        Then, we'll put it in a list of date/value pairs and print it out
        Calendar is hardcoded to TARGET to keep life simple
        '''
        timeSteps = VARUtilities.VARTimePeriodsAndSteps()
        timeSteps.generate(start = self._parameters.start, 
                           end = self._parameters.end, 
                           num = 1, 
                           term = Enum.TimePeriod('D'), 
                           calendar = Calendar.createCalendar('TARGET'))
        for item in timeSteps.timeSteps:
            asOf = item
            value = 0.0
            for portfolio in self._parameters.portfolios:
                value += self._value(portfolio=portfolio, asOf=asOf)
            self._results.append((item,value))
        
class TimeSeriesNPVCalculatorParameters(CalculatorParameters):
        def __init__(self, start=None, end=None, marketId=None, portfolios=None):
            self.start = start
            self.end = end
            self.marketId = marketId
            self.portfolios = portfolios
          
def main():
    parameters = TimeSeriesNPVCalculatorParameters(start=Date(month=7,day=25,year=2013),
                                                   end=Date(pythonDate=datetime.date.today()),
                                                   marketId='EOD',
                                                   portfolios=Portfolio.objects.filter(user='cmt'))
    calculator = TimeSeriesNPVCalculator(parameters=parameters)
    calculator.calc()
    print calculator.prettyPrint()
    
if __name__ == "__main__":
    main()