'''
Created on Sep 19, 2012

@author: Capital Market Tools
'''
from settings import ROOT_PATH
from src.models import Equity, StockPrice, InterestRateCurve, InterestRate
from src.models import Location, UserProfile, TCBond, Identifier,Portfolio
from src.models import ModelPosition, HvarConfiguration, Transaction, Batch
from src.models import BondOAS, SwaptionVolatilitySurface, SwaptionVolatility
from src.bo.Enum import TransactionType, PositionType, BondIdentifierType
from src.bo import Enum, VARUtilities
from src.bo.Date import Date
from src.bo.utilities import MarketDataLoader, FREDLoader
from src.bo.static import Calendar
from datetime import date
from django.contrib.auth.models import User

class DBInitialData(object):
    '''
    Some data is in a fixture to initialize django such as user, userprofile, site...
    This class is used to load a reasonable amount of application data into the system
    '''

    def dataForSuccessfulTest(self):
        '''
        This saves all data so that system tests run successfully
        Pricing date is 9/12/2011 with market data id TEST1
        '''
        testDatePython = date(month=9,day=12,year=2011)
        testDate = Date(month=9,day=12,year=2011)
        testFirstDate = Date(month=8,day=30,year=2011)
        
        if not Location.objects.filter(name='Test1').exists():
            location = Location()
            location.name = 'Test1'
            location.pricingDate = date(month=9,day=12,year=2011)
            location.save()
        location = Location.objects.get(name='Test1')
            
        if not User.objects.filter(username='root').exists():
            user = User.objects.create_user(username='root',email='capitalmarkettools.org@gmail.com',\
                                            password='root')
            user.is_staff = True
            user.is_superuser = True
            user.save()

        if not User.objects.filter(username='cmt1').exists():
            User.objects.create_user(username='cmt1',email='capitalmarkettools.org@gmail.com',\
                                     password='cmt1')

        if not User.objects.filter(username='test1').exists():
            User.objects.create_user(username='test1',email='capitalmarkettools.org@gmail.com',\
                                     password='test1')

        if not User.objects.filter(username='demo').exists():
            User.objects.create_user(username='demo',email='capitalmarkettools.org@gmail.com',\
                                     password='demo1')

        user1 = User.objects.get(username='root')
        if not UserProfile.objects.filter(user=user1).exists():
            up1 = UserProfile()
            up1.user = user1
            up1.location = location
            up1.marketId = 'EOD'
            up1.save()
            
        user2 = User.objects.get(username='cmt1')
        if not UserProfile.objects.filter(user=user2).exists():
            up2 = UserProfile()
            up2.user = user2
            up2.location = location
            up2.marketId = 'EOD'
            up2.save()

        user3 = User.objects.get(username='test1')
        if not UserProfile.objects.filter(user=user3).exists():
            up3 = UserProfile()
            up3.user = user3
            up3.location = location
            up3.marketId = 'TEST1'
            up3.save()

        user4 = User.objects.get(username='demo')
        if not UserProfile.objects.filter(user=user4).exists():
            up4 = UserProfile()
            up4.user = user4
            up4.location = location
            up4.marketId = 'DEMO'
            up4.save()
        
        if not TCBond.objects.filter(name='TEST1').exists():
            bond = TCBond()
            bond.name = 'TEST1'
            bond.ccy = 'USD'
            cusip = Enum.BondIdentifierType('CUSIP') 
            if not Identifier.objects.filter(name='123456789', type=cusip):
                identifier = Identifier()
                identifier.name='123456789'
                identifier.type=cusip
                identifier.save()
            identifier = Identifier.objects.get(name='123456789', type=cusip)  
            bond.identifiers = identifier
            bond.startDate = Date(month=9,day=12,year=2010).toPythonDate()
            bond.endDate = Date(month=9,day=12,year=2020).toPythonDate()
            bond.coupon = 0.01
            bond.basis = '30360'
            bond.paymentFrequency = Enum.Frequency('S')
            bond.paymentRollRule = Enum.Roll('MF')
            bond.paymentCalendar = Calendar.createCalendar('US')
            bond.assetType = Enum.AssetType('NYMUNIBOND')
            bond.save()

        if not Equity.objects.filter(ticker='TEST1').exists():
            equity = Equity()
            equity.ticker = 'TEST1'
            equity.assetType = Enum.AssetType('EQUITYUS')
            equity.save()
        equity = Equity.objects.get(ticker='TEST1')
        stockPrice = StockPrice()
        stockPrice.equity = equity
        stockPrice.pricingDate = testDate
        stockPrice.marketId = 'TEST1'
        stockPrice.mid = 123.45
        stockPrice.save()
        equity = Equity.objects.get(ticker='TEST1')
        stockPrice = StockPrice()
        stockPrice.equity = equity
        stockPrice.pricingDate = testFirstDate
        stockPrice.marketId = 'TEST1'
        stockPrice.mid = 123.44
        stockPrice.save()
        if not Equity.objects.filter(ticker='TEST2').exists():
            equity = Equity()
            equity.ticker = 'TEST2'
            equity.assetType = Enum.AssetType('EQUITYUS')
            equity.save()
        equity = Equity.objects.get(ticker='TEST2')
        stockPrice = StockPrice()
        stockPrice.equity = equity
        stockPrice.pricingDate = testDate
        stockPrice.marketId = 'TEST1'
        stockPrice.mid = 543.21
        stockPrice.save()
        equity = Equity.objects.get(ticker='TEST2')
        stockPrice = StockPrice()
        stockPrice.equity = equity
        stockPrice.pricingDate = testFirstDate
        stockPrice.marketId = 'TEST1'
        stockPrice.mid = 543.11
        stockPrice.save()
        
        if not Portfolio.objects.filter(name='TEST1', user='test1').exists():
            portfolio =Portfolio()
            portfolio.name = 'TEST1'
            portfolio.user = 'test1'
            portfolio.save()
        portfolio =Portfolio.objects.get(name='TEST1', user='test1')
        
        if not ModelPosition.objects.filter(asOf=testDate, portfolio=portfolio, 
                                       positionType = Enum.PositionType('EQUITY'),
                                       ticker = 'TEST1', amount = 100.0).exists():
            position = ModelPosition()
            position.asOf=testDate
            position.portfolio = portfolio
            position.positionType = Enum.PositionType('EQUITY')
            position.ticker = 'TEST1'
            position.amount = 100.0
            position.save()

        if not ModelPosition.objects.filter(asOf=testDate, portfolio=portfolio, 
                                       positionType = Enum.PositionType('EQUITY'),
                                       ticker = 'TEST2', amount = 100.0).exists():
            position = ModelPosition()
            position.asOf=testDate
            position.portfolio = portfolio
            position.positionType = Enum.PositionType('EQUITY')
            position.ticker = 'TEST2'
            position.amount = 100.0
            position.save()

        if not ModelPosition.objects.filter(asOf=testDate, portfolio=portfolio, 
                                       positionType = Enum.PositionType('BOND'),
                                       ticker = 'TEST1', amount = 100.0).exists():
            position = ModelPosition()
            position.asOf=testDate
            position.portfolio = portfolio
            position.positionType = Enum.PositionType('BOND')
            position.ticker = 'TEST1'
            position.amount = 100.0
            position.save()
       
        if not ModelPosition.objects.filter(asOf=testFirstDate, portfolio=portfolio, 
                                       positionType = Enum.PositionType('EQUITY'),
                                       ticker = 'TEST1', amount = 100.0).exists():
            position = ModelPosition()
            position.asOf=testFirstDate
            position.portfolio = portfolio
            position.positionType = Enum.PositionType('EQUITY')
            position.ticker = 'TEST1'
            position.amount = 100.0
            position.save()

        if not ModelPosition.objects.filter(asOf=testFirstDate, portfolio=portfolio, 
                                       positionType = Enum.PositionType('EQUITY'),
                                       ticker = 'TEST2', amount = 100.0).exists():
            position = ModelPosition()
            position.asOf=testFirstDate
            position.portfolio = portfolio
            position.positionType = Enum.PositionType('EQUITY')
            position.ticker = 'TEST2'
            position.amount = 100.0
            position.save()

        if not ModelPosition.objects.filter(asOf=testFirstDate, portfolio=portfolio, 
                                       positionType = Enum.PositionType('BOND'),
                                       ticker = 'TEST1', amount = 100.0).exists():
            position = ModelPosition()
            position.asOf=testFirstDate
            position.portfolio = portfolio
            position.positionType = Enum.PositionType('BOND')
            position.ticker = 'TEST1'
            position.amount = 100.0
            position.save()
            
        if not ModelPosition.objects.filter(asOf=testFirstDate, portfolio=portfolio, 
                                       positionType = Enum.PositionType('CASH'),
                                       ticker = 'Cash', amount = 1000.0).exists():
            position = ModelPosition()
            position.asOf=testFirstDate
            position.portfolio = portfolio
            position.positionType = Enum.PositionType('CASH')
            position.ticker = 'Cash'
            position.amount = 1000.0
            position.save()
            
        curve = InterestRateCurve()
        curve.ccy = 'USD'
        curve.index = Enum.Index('LIBOR')
        curve.term = Enum.TimePeriod('M')
        curve.numTerms = 3
        curve.pricingDate =testDate
        curve.marketId = 'TEST1'

        curve.addRate(InterestRate(type='Deposit', term=Enum.TimePeriod('M'),
                                   numTerms=1,mid=0.01,curve=curve))
        curve.addRate(InterestRate(type='Deposit', term=Enum.TimePeriod('M'),
                                   numTerms=3,mid=0.01,curve=curve))
        curve.addRate(InterestRate(type='Swap', term=Enum.TimePeriod('Y'),
                                   numTerms=1,mid=0.01,curve=curve))
        curve.addRate(InterestRate(type='Swap', term=Enum.TimePeriod('Y'),
                                   numTerms=5,mid=0.01,curve=curve))
        curve.addRate(InterestRate(type='Swap', term=Enum.TimePeriod('Y'),
                                   numTerms=10,mid=0.01,curve=curve))
        curve.addRate(InterestRate(type='Swap', term=Enum.TimePeriod('Y'),
                                   numTerms=30,mid=0.01,curve=curve))
        curve.save()

        curve = InterestRateCurve()
        curve.ccy = 'USD'
        curve.index = Enum.Index('LIBOR')
        curve.term = Enum.TimePeriod('M')
        curve.numTerms = 3
        curve.pricingDate = testFirstDate
        curve.marketId = 'TEST1'

        curve.addRate(InterestRate(type='Deposit', term=Enum.TimePeriod('M'),
                                   numTerms=1,mid=0.01,curve=curve))
        curve.addRate(InterestRate(type='Deposit', term=Enum.TimePeriod('M'),
                                   numTerms=3,mid=0.01,curve=curve))
        curve.addRate(InterestRate(type='Swap', term=Enum.TimePeriod('Y'),
                                   numTerms=1,mid=0.01,curve=curve))
        curve.addRate(InterestRate(type='Swap', term=Enum.TimePeriod('Y'),
                                   numTerms=5,mid=0.01,curve=curve))
        curve.addRate(InterestRate(type='Swap', term=Enum.TimePeriod('Y'),
                                   numTerms=10,mid=0.01,curve=curve))
        curve.addRate(InterestRate(type='Swap', term=Enum.TimePeriod('Y'),
                                   numTerms=30,mid=0.01,curve=curve))
        curve.save()
        
        if not SwaptionVolatilitySurface.objects.filter(ccy=Enum.Currency('USD'), index=Enum.Index('LIBOR'), term=Enum.TimePeriod('M'), numTerms=3, 
                                                        pricingDate=testDate, marketId='TEST1'):
            #Special case where I just append the vols. Should use a function
            vols = SwaptionVolatilitySurface(ccy=Enum.Currency('USD'), index=Enum.Index('LIBOR'), term=Enum.TimePeriod('M'), numTerms=3, 
                                             pricingDate=testDate, marketId='TEST1')
            volPoints = []
            volPoints.append(SwaptionVolatility(expiryTerm=Enum.TimePeriod('Y'), expiryNumTerms=1, underlyingTerm=Enum.TimePeriod('Y'),
                                                underlyingNumTerms=3, mid=0.40, surface=vols))
            volPoints.append(SwaptionVolatility(expiryTerm=Enum.TimePeriod('Y'), expiryNumTerms=3, underlyingTerm=Enum.TimePeriod('Y'),
                                                underlyingNumTerms=3, mid=0.45, surface=vols))
            volPoints.append(SwaptionVolatility(expiryTerm=Enum.TimePeriod('Y'), expiryNumTerms=1, underlyingTerm=Enum.TimePeriod('Y'),
                                                underlyingNumTerms=5, mid=0.5, surface=vols))
            volPoints.append(SwaptionVolatility(expiryTerm=Enum.TimePeriod('Y'), expiryNumTerms=3, underlyingTerm=Enum.TimePeriod('Y'),
                                                underlyingNumTerms=5, mid=0.55, surface=vols))
            vols.addVolatilities(volPoints)
            vols.save()
            
        if not BondOAS.objects.filter(tCBond=TCBond.objects.get(name='TEST1'),pricingDate=testDate,
                                   marketId='TEST1'):
            bondOAS = BondOAS(tCBond=TCBond.objects.get(name='TEST1'),pricingDate=testDate,
                              marketId='TEST1',mid=0.0012)
            bondOAS.save()
        #done for only one test BondPositionTest.testLoadAndSaveMarketData
        if not BondOAS.objects.filter(tCBond=TCBond.objects.get(name='TEST1'),pricingDate=Date(month=1,day=1,year=2009),
                                      marketId='EOD'):
            bondOAS = BondOAS(tCBond=TCBond.objects.get(name='TEST1'),pricingDate=Date(month=1,day=1,year=2009),
                              marketId='EOD',mid=0.01)
            bondOAS.save()
        #now load zero oas for all dates we do testing
        timePeriods = VARUtilities.VARTimePeriodsAndSteps()
        timePeriods.generate(start = Date(month=8,day=30,year=2011), end = Date(month=9,day=12,year=2011), 
                             num = 1, term = Enum.TimePeriod('D'), calendar = Calendar.US())
        for timeStep in timePeriods.timeSteps:
            if not BondOAS.objects.filter(tCBond=TCBond.objects.get(name='TEST1'), pricingDate=timeStep, marketId='TEST1'):
                bondOAS = BondOAS(tCBond=TCBond.objects.get(name='TEST1'), pricingDate=timeStep, marketId='TEST1',mid=0.0)
                bondOAS.save()
        
        fileLoader = MarketDataLoader.EquityPriceLoader()
        fileLoader.loadStockPriceFromCSVFile(ROOT_PATH+'/misc/data/StockPricesForHVaRTests.csv')
        fileLoader.loadInterestRateFromCSVFile(ROOT_PATH+'/misc/data/InterestRatesForHVaRTests.csv')

        if not HvarConfiguration.objects.filter(name='TEST1').exists():
            config = HvarConfiguration()
            config.name = 'TEST1'
            config.startDate = Date(month=8,day=30,year=2011).toPythonDate()
            config.endDate = Date(month=9,day=12,year=2011).toPythonDate()
            config.stepSize = 1
            config.stepUnit = Enum.TimePeriod('D')
            config.calendar = Calendar.US()
            config.confLevel = 0.95
            config.marketId = 'TEST1'
            config.save()

    def moreData(self):
        '''
        Some other data
        '''
        
        tickers = ['ALU','C','CMCSA','CSCO','GE','HD','IBM','INTC','JNJ','LSI','MRK','MSFT',
                   'PFE','T','TWX','VZ','WMT', 'GOOG', 'IBM', 'GS']
        for ticker in tickers:
            if not Equity.objects.filter(ticker=ticker).exists():
                equity = Equity()
                equity.ticker = ticker
                equity.assetType = Enum.AssetType('EQUITYUS')
                equity.save()
        
        #Do not have interest rate data for this early
#        name = '1987 Crash'
#        if not HvarConfiguration.objects.filter(name=name).exists():
#            config = HvarConfiguration()
#            config.name = name
#            config.startDate = Date(month=8,day=14,year=1987).toPythonDate()
#            config.endDate = Date(month=1,day=29,year=1988).toPythonDate()
#            config.stepSize = 1
#            config.stepUnit = Enum.TimePeriod('D')
#            config.calendar = Calendar.US()
#            config.confLevel = 0.95
#            config.marketId = 'TEST1'
#            config.save()

        name = '2001 Tech Crash'
        if not HvarConfiguration.objects.filter(name=name).exists():
            config = HvarConfiguration()
            config.name = name
            #Use this date becuase FRED swap data available as 7/3/2000
            config.startDate = Date(month=7,day=3,year=2000).toPythonDate()
            config.endDate = Date(month=7,day=3,year=2003).toPythonDate()
            config.stepSize = 1
            config.stepUnit = Enum.TimePeriod('M')
            config.calendar = Calendar.US()
            config.confLevel = 0.95
            config.marketId = 'TEST1'
            config.save()

        name = '2008 Real Estate Crash'
        if not HvarConfiguration.objects.filter(name=name).exists():
            config = HvarConfiguration()
            config.name = name
            config.startDate = Date(month=6,day=15,year=2007).toPythonDate()
            config.endDate = Date(month=6,day=15,year=2009).toPythonDate()
            config.stepSize = 1
            config.stepUnit = Enum.TimePeriod('M')
            config.calendar = Calendar.US()
            config.confLevel = 0.95
            config.marketId = 'TEST1'
            config.save()

#        fredLoader = FREDLoader.FREDLoader()
#        fredLoader.loadAllLiborCurves(marketId='EOD')

    def dataForProductionStart(self): 
        #Setup initial data for Tim's portfolios as of 7/24/13        
        productionStartDate = Date(month=7,day=25,year=2013)
        
        if not Batch.objects.filter(batchDate=productionStartDate):
            batch = Batch()
            batch.batchDate = productionStartDate
            batch.save()
        
        if not Location.objects.filter(name='Manhasset').exists():
            location = Location()
            location.name = 'Manhasset'
            location.pricingDate = date(month=7,day=25,year=2013)
            location.save()
        
        if not User.objects.filter(username='cmt').exists():
            #Enter email password
            User.objects.create_user(username='cmt',email='capitalmarkettools.org@gmail.com',\
                                     password='XXX')
            
        cmt = User.objects.get(username='cmt')
        if not UserProfile.objects.filter(user=cmt).exists():
            up2 = UserProfile()
            up2.user = cmt
            up2.location = Location.objects.get(name='Manhasset')
            up2.marketId = 'EOD'
            up2.save()
        #if it exists then make sure Location is Manhasset
        else:
            profile = UserProfile.objects.get(user=cmt)
            profile.location = Location.objects.get(name='Manhasset')
            profile.marketId = 'EOD'
            profile.save()

        #Setup portfolios
        portfolioData = (['401K','cmt'],['ChaseIRA','cmt'],
                         ['TDIRA','cmt'],['TDPostTaxIRA','cmt'],
                         ['Just2Trade','cmt'],['TDEmergency','cmt'])
        for p in portfolioData:
            if not Portfolio.objects.filter(name=p[0],user=p[1]):
                portfolio =Portfolio()
                portfolio.name = p[0]
                portfolio.user = p[1]
                portfolio.save()

        #Setup Equities and Prices as of productionStartDate
        dataSet = (('NEIAX',32.57),('PTTDX',10.78),('EFA',61.06),
                   ('GSG',32.67),('SAN-E',26.7301),('VWO',40.19),
                   ('VNQ', 71.17))
        for data in dataSet:
            if not Equity.objects.filter(ticker=data[0]).exists():
                equity = Equity()
                equity.ticker = data[0]
                equity.assetType = Enum.AssetType('EQUITYUS')
                equity.save()
            equity = Equity.objects.get(ticker=data[0])
            stockPrice = StockPrice()
            stockPrice.equity = equity
            stockPrice.pricingDate = productionStartDate
            stockPrice.marketId = 'EOD'
            stockPrice.mid = data[1]
            stockPrice.save()

        #Setup Bond identifiers and TCBonds as of productionStartDate
        dataSet = (('PortAuth_4.00_JAN42','73358WGG3',Date(month=1,day=15,year=2012),Date(month=1,day=15,year=2042),0.04,),)
        for data in dataSet:
            if not Identifier.objects.filter(name=data[1],type=BondIdentifierType('CUSIP')):
                identifier = Identifier()
                identifier.name = data[1]
                identifier.type = BondIdentifierType('CUSIP')
                identifier.save()
        for data in dataSet:
            if not TCBond.objects.filter(name=data[0]):
                tcBond = TCBond()
                tcBond.name = data[0]
                tcBond.identifiers = Identifier.objects.get(name=data[1],type=BondIdentifierType('CUSIP'))
                tcBond.startDate = data[2].toPythonDate()
                tcBond.endDate = data[3].toPythonDate()
                tcBond.coupon = data[4]
                tcBond.assetType = Enum.AssetType('NYMUNIBOND')
                tcBond.save()
 
        #Setup OAS for production start date
        if not BondOAS.objects.filter(tCBond=TCBond.objects.get(name='PortAuth_4.00_JAN42'), marketId='EOD',pricingDate=productionStartDate):
            bondOAS = BondOAS(tCBond=TCBond.objects.get(name='PortAuth_4.00_JAN42'), marketId='EOD',pricingDate=productionStartDate,mid=0.014)
            bondOAS.save()
            
        #Setup Rates
        fredLoader = FREDLoader.FREDLoader()
        fredLoader.loadLiborCurvesForSpecificDates(marketId='EOD', datesToLoadFor=[productionStartDate])
       
        #Setup transactions 
        dataSet = (('401K','INIT','EQUITY','NEIAX',8758.407),
                    ('401K','INIT','EQUITY','PTTDX',10746.441),
                    ('ChaseIRA','INIT','EQUITY','EFA',633.37038),
                    ('TDIRA','INIT','EQUITY','EFA',47),
                    ('TDIRA','INIT','EQUITY','GSG',610),
                    ('TDIRA','INIT','EQUITY','VWO',1050),
                    ('TDIRA','INIT','CASH','Cash',11151.23),
                    ('TDPostTaxIRA','INIT','EQUITY','EFA',560),
                    ('TDPostTaxIRA','INIT','EQUITY','VNQ',170),
                    ('TDPostTaxIRA','INIT','CASH','Cash',951.33),
                    ('Just2Trade','INIT','EQUITY','GSG',300),
                    ('Just2Trade','INIT','EQUITY','VWO',430),
                    ('TDEmergency','INIT','BOND','PortAuth_4.00_JAN42',100),
                    ('TDEmergency','INIT','CASH','Cash',201.01))
        
        for data in dataSet:
            if not Transaction.objects.filter(portfolio=Portfolio.objects.get(name=data[0]),
                                              transactionType=TransactionType(data[1]),
                                              positionType=PositionType(data[2]),
                                              ticker=data[3],
                                              amount=data[4],
                                              transactionDate = productionStartDate,
                                              effectiveDate = productionStartDate):
                transaction = Transaction()
                transaction.portfolio =Portfolio.objects.get(name=data[0])
                transaction.transactionType = TransactionType(data[1])
                transaction.positionType = PositionType(data[2])
                transaction.ticker = data[3]
                transaction.amount = data[4]
                transaction.transactionDate = productionStartDate
                transaction.effectiveDate = productionStartDate
                transaction.reflectedInPosition = False
                transaction.save()
        
def main():
    init = DBInitialData()
    init.dataForSuccessfulTest()
    init.dataForProductionStart() 
    init.moreData()

if __name__ == "__main__":
    main()        
