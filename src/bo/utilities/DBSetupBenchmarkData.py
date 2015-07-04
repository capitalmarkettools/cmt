'''
Created on Sep 19, 2012

@author: Capital Market Tools
'''
from src.models import Equity, StockPrice, InterestRateCurve, InterestRate
from src.models import Location, UserProfile, TCBond, Identifier,Portfolio
from src.models import ModelPosition, HvarConfiguration, Transaction, Batch
from src.models import BondOAS
from src.bo.Enum import TransactionType, PositionType, BondIdentifierType
from src.bo import Enum, VARUtilities
from src.bo.Date import Date
from src.bo.utilities import MarketDataLoader, FREDLoader
from src.bo.static import Calendar
from datetime import date
from django.contrib.auth.models import User

class DBSetupBenchmarkData(object):
    '''
    Sets up everything that is required to run Benchmark analysis. 
    It sets up user, portfolio
    '''

    def setupData(self):
        productionStartDate = Date(month=7,day=25,year=2013)
        lastLoadDate = Date(month=10,day=14,year=2013)
        loadDate = productionStartDate
        
        if not Location.objects.filter(name='Benchmark').exists():
            location = Location()
            location.name = 'Benchmark'
            location.pricingDate = date(month=10,day=14,year=2013)
            location.save()
        location = Location.objects.get(name='Benchmark')
            
        if not User.objects.filter(username='benchmark').exists():
            user = User.objects.create_user(username='benchmark',email='capitalmarkettools.org@gmail.com',\
                                            password='benchmark')
            user.is_staff = True
            user.is_superuser = True
            user.save()

        user1 = User.objects.get(username='benchmark')
        if not UserProfile.objects.filter(user=user1).exists():
            up1 = UserProfile()
            up1.user = user1
            up1.location = location
            up1.marketId = 'EOD'
            up1.save()

        equities = Equity.objects.all()
        for equity in equities:
#            print equity
            if not Portfolio.objects.filter(name=equity.ticker, user='benchmark').exists():
                portfolio =Portfolio()
                portfolio.name = equity.ticker
                portfolio.user = 'benchmark'
                portfolio.save()
            portfolio = Portfolio.objects.get(name=equity.ticker, user='benchmark')
 
            timeSteps = VARUtilities.VARTimePeriodsAndSteps()
            timeSteps.generate(start=productionStartDate, end=lastLoadDate, num=1, 
                               term=Enum.TimePeriod('D'), calendar=Calendar.Target())
            for loadDate in timeSteps.timeSteps:
                if not ModelPosition.objects.filter(asOf=loadDate, portfolio=portfolio, 
                                                    positionType = Enum.PositionType('EQUITY'),
                                                    ticker = equity.ticker, amount = 100.0).exists():
                    position = ModelPosition()
                    position.asOf=loadDate
                    position.portfolio = portfolio
                    position.positionType = Enum.PositionType('EQUITY')
                    position.ticker = equity.ticker
                    position.amount = 100.0
                    position.save()

def main():
    init = DBSetupBenchmarkData()
    init.setupData()

if __name__ == "__main__":
    main()        