from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
import modelFields
from src.bo.Enum import Currency, Frequency, Roll, TimePeriod, Index, PositionType, TransactionType
from src.bo.static import Calendar
from src.bo import cmt, Shift, Enum, Date, ErrorHandling
from src.bo.decorators import log
import QuantLib

class Portfolio(models.Model):
    name = models.CharField(max_length=200)
    #each portfolio belongs to a user
    #TODO: Make this a foreign key field
    user = models.CharField(max_length=100)

    def __init__(self, *args, **kwargs):
        #This positions is not models.ModelPosition but bo.instruments.Position
        self.positions = []
        super(Portfolio, self).__init__(*args, **kwargs)

    class Meta:
        db_table = 'cmt_portfolio'
        unique_together = ('name', 'user')
    def __str__(self):
        return str(self.name)
    def __unicode__(self):
#        return u"%s/%s" % (self.name, self.user)
        return u"%s/%s" % (self.name, self.user)
    
    def addPosition(self, position):
        if type(position) is ModelPosition:
            raise ErrorHandling.ParameterException("position must be Position and not ModelPosition")
        self.positions.append(position)
               
#     def loadPositions(self, asOf=None):
#         '''
#         deletes all positions that are currently in object and loads new positions from DB
#         asOf is Date() class
#         '''
#         if asOf == None:
#             raise ErrorHandling.ParameterException("asOf is required parameter")
#         self.positions = []
#         modelPositions = ModelPosition.objects.filter(portfolio=self, asOf=asOf)
#         for modelPosition in modelPositions:
#             position = CreatePosition(modelPosition)
#             self.addPosition(position)
            
    def NPV(self, pricingDate=None, marketId=None):
        if pricingDate==None or marketId==None:
            raise ErrorHandling.OtherException('pricingDate and marketId must be passed')
        npv = 0
        for position in self.positions:
            #print position
            #print position.__class__
            #print position.NPV(pricingDate=pricingDate, marketId=marketId)
            npv = npv + position.NPV(pricingDate=pricingDate, marketId=marketId)
        return npv

class ModelPosition(models.Model):
    portfolio = models.ForeignKey(Portfolio)
    positionType = modelFields.PositionTypeField(max_length=20)
    ticker = models.CharField(max_length=200, help_text='Equity, Bond or Swap identifier. Set Cash for cash')
    amount = models.FloatField()
    asOf = modelFields.DateField()
    class Meta:
        db_table = 'cmt_position'
    def __unicode__(self):
        return "%s/%s/%s/%s/%s" % (self.portfolio,self.positionType,self.ticker,self.amount,self.asOf)
    
class Transaction(models.Model):
    portfolio = models.ForeignKey(Portfolio)
    transactionType = modelFields.TransactionTypeField(max_length=20)    
    positionType = modelFields.PositionTypeField(max_length=20)    
    ticker = models.CharField(max_length=200, help_text='Equity, Bond or Swap identifier. Set Cash for cash')
    amount = models.FloatField()
    transactionDate = modelFields.DateField()
    effectiveDate = modelFields.DateField()
    reflectedInPosition = models.BooleanField(default=False)

    class Meta:
        db_table = 'cmt_transaction'
    def __unicode__(self):
        return "%s/%s/%s/%s/%s/%s/%s" % (self.portfolio,self.transactionType,self.positionType,self.ticker,\
                                      self.amount,self.transactionDate, self.effectiveDate)
        
    def relatedPositions(self):
        '''
        Returns all positions that are stored in the DB that are affected by this transaction
        If there is no position then save a new one and call function again
        '''
        #Then do all positions that are in the future and that are affected. Think about if this is really needed
        positions = ModelPosition.objects.filter(portfolio=self.portfolio, positionType=self.positionType,
                                            ticker=self.ticker, asOf__gte=self.transactionDate)
        if len(positions) == 0:
            position = ModelPosition()
            position.portfolio = self.portfolio
            position.positionType = self.positionType
            position.ticker = self.ticker
            position.amount = 0
            position.asOf = self.transactionDate
            position.save()
            return self.relatedPositions()
        return positions
            
    def updatePositionAmount(self, position=None):
        if self.transactionType == TransactionType('BUY') or self.transactionType == TransactionType('ADD'):
            position.amount = position.amount + self.amount
        elif self.transactionType == TransactionType('SELL') or self.transactionType == TransactionType('REMOVE'):
            position.amount = position.amount - self.amount
        elif self.transactionType == TransactionType('INIT'):
            position.amount = self.amount
        else:
            pass
    
class Equity(models.Model):
    ticker = models.CharField(max_length=200, unique=True)
    assetType = modelFields.AssetTypeField(max_length=30)    
    class Meta:
        db_table = 'cmt_equity'
    def __unicode__(self):
        return "%s" % (self.ticker)
    
    def save(self):
        exists = Equity.objects.filter(ticker=self.ticker)
        if not exists:
            super(Equity, self).save()
        else:
            pass
            
class Location(models.Model):
    """ Specifies Location a process runs in 
    Location contains the pricing date
    """
    name = models.CharField(max_length=200, unique=True)
    pricingDate = models.DateField()
    class Meta:
        db_table = 'cmt_location'
    def __unicode__(self):
        return self.name
    
class UserProfile(models.Model):
    """ Stores user profile
    User profile contains the location the user is located 
    """
    user = models.OneToOneField(User, unique=True, editable=False)
    location = models.ForeignKey(Location, default=1)
    marketId = models.CharField(max_length=20, default='EOD')
    class Meta:
        db_table = 'cmt_userprofile'
    def __unicode__(self):
        return self.user.username

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)
        if created == True:
            defaultLocation = Location.objects.get(name='Test1')
            profile.location = defaultLocation
        profile.save()
post_save.connect(create_user_profile, sender=User)

class HvarConfiguration(models.Model):
    """ Stores parameters to run HVaR analysis
    Should have a descriptive name so that users can just pick Name
    """
    name = models.CharField(max_length=100, unique=True)
    startDate = models.DateField()
    endDate = models.DateField()
    stepSize = models.IntegerField()
    stepUnit = modelFields.TimePeriodField(max_length=20)
    calendar = modelFields.CalendarField(max_length=10)
    confLevel = models.FloatField()
    #TODO: Make this a choice field
    marketId = models.CharField(max_length=20, blank=True)
    class Meta:
        db_table = 'cmt_hvarconfiguration'
    def __unicode__(self):
        return self.name

class Identifier(models.Model):
    ''' This is an identifier. Becuase there are many identifiers the class consists of
    a type and value. It can be used for all kind of classes
    The class that uses identifiers should include the identifiers class as a 
    foreign key. Django will provide a unique id
    '''
    name = models.CharField(max_length=20)
    type = modelFields.BondIdentifierTypeField(max_length=20)

    class Meta:
        db_table = 'cmt_identifier'
        unique_together = ('name', 'type')
        
    def __unicode__(self):
        return "%s/%s" % (self.type, self.name)
    
class TCBond(models.Model):
    '''
    Warning that basis is just a char. There is some issue with BasisField
    '''
    name = models.CharField(max_length=100, unique=True)
    ccy = modelFields.CurrencyField(max_length=20, default=Currency('USD'))
    identifiers = models.ForeignKey(Identifier)
    startDate = models.DateField()
    endDate = models.DateField()
    #maturity in in A/365 basis
    #maturity = models.FloatField()
    #only fixed coupons allowed
    coupon = models.FloatField()
    basis = modelFields.BasisField(max_length=8, default='30360')
    paymentFrequency = modelFields.FrequencyField(max_length=20, 
                                                  default=Frequency('S'))
    paymentRollRule = modelFields.RollField(max_length=20,
                                            default=Roll('MF'))
    paymentCalendar = modelFields.CalendarField(max_length=20,
                                                default=Calendar.createCalendar('US'))
    assetType = modelFields.AssetTypeField(max_length=20)    

    class Meta:
        db_table = 'cmt_tcbond'
    def __unicode__(self):
        return self.name

class TCSwap(models.Model):
    #name is a system generated id to link the position to the tc of swap
    name = models.CharField(max_length=100, unique=True)
    ccy = modelFields.CurrencyField(max_length=20, default=Currency('USD'))
    startDate = models.DateField()
    endDate = models.DateField()
    #maturity in in A/365 basis
    #maturity = models.FloatField()
    fixedCoupon = models.FloatField(default=0.01)
    fixedBasis = modelFields.BasisField(max_length=20, 
                                          default='30360')
    fixedPaymentFrequency = modelFields.FrequencyField(max_length=20, default=Frequency('S'))
    fixedPaymentRollRule = modelFields.RollField(max_length=20, default=Roll('MF'))
    fixedPaymentCalendar = modelFields.CalendarField(max_length=20, 
                                                       default=Calendar.createCalendar('US'))
    floatingIndex = modelFields.IndexField(max_length=20, default=Index('LIBOR'))
    floatingIndexTerm = modelFields.TimePeriodField(max_length=20, default=TimePeriod('M'))
    floatingIndexNumTerms = models.IntegerField(default=3)
    floatingSpread = models.FloatField(default=0.0)
    floatingBasis = modelFields.BasisField(max_length=20, 
                                             default='A360')
    floatingPaymentFrequency = modelFields.FrequencyField(max_length=20, default=Frequency('Q'))
    floatingPaymentRollRule = modelFields.RollField(max_length=20, default=Roll('MF'))
    floatingPaymentCalendar = modelFields.CalendarField(max_length=20,
                                                          default=Calendar.createCalendar('US'))
    floatingResetFrequency = modelFields.FrequencyField(max_length=20, default=Frequency('S'))
    floatingResetRollRule = modelFields.RollField(max_length=20, default=Roll('MF'))
    floatingResetCalendar = modelFields.CalendarField(max_length=20,
                                                        default=Calendar.createCalendar('US'))
    
    class Meta:
        db_table = 'cmt_tcswap'
    def __unicode__(self):
        return self.name
    
class InterestRate(models.Model):
    type = models.CharField(max_length=20)
    term = modelFields.TimePeriodField(max_length=20)
    numTerms = models.IntegerField()
    mid = models.FloatField()
    curve = models.ForeignKey('InterestRateCurve')
    class Meta:
        db_table = 'cmt_interestrate'
        unique_together = ('type', 'term', 'numTerms', 'curve')
    def __unicode__(self):
        return "%s/%s/%s/%s" % (self.type, self.term, self.numTerms, self.curve)
    def __str__(self):
        return "%s/%s/%s/%s/%s" % (self.type, self.term, self.numTerms, self.mid, self.curve)
    
class InterestRateCurve(models.Model):
    ccy = modelFields.CurrencyField(max_length=20)
    index = modelFields.IndexField(max_length=20, default=Index('LIBOR'))
    term = modelFields.TimePeriodField(max_length=20)
    numTerms = models.IntegerField()
    pricingDate = modelFields.DateField()
    marketId = models.CharField(max_length=20, blank=True, default='')
    class Meta:
        db_table = 'cmt_interestratecurve'
        unique_together = ('ccy', 'index', 'term', 'numTerms', 'pricingDate', 'marketId')

    def __init__(self, *args, **kwargs):
        self.rates = []
        super(InterestRateCurve, self).__init__(*args, **kwargs)
    
    def __unicode__(self):
        return "%s/%s/%s/%s/%s/%s" % (self.ccy, self.index, self.term, 
                                      self.numTerms, self.pricingDate, self.marketId)
        
    def getRates(self):
        return self.rates
    
    @log
    def save(self):
        '''
        if curve does not exists then save the curve. 
        otherwise delete the DB curve rates and save the new rates
        ''' 
        try:
            curve = InterestRateCurve.objects.get(ccy=self.ccy, index=self.index,
                                                  term=self.term, numTerms=self.numTerms,
                                                  pricingDate=self.pricingDate, marketId=self.marketId)
            oldRates = curve.interestrate_set.all()
            for oldRate in oldRates:
                oldRate.delete()
            for rate in self.rates:
                rate.curve = curve
                rate.save()
        except InterestRateCurve.DoesNotExist:
            super(InterestRateCurve, self).save()
            curve = InterestRateCurve.objects.get(ccy=self.ccy, index=self.index,
                                                  term=self.term, numTerms=self.numTerms,
                                                  pricingDate=self.pricingDate, marketId=self.marketId)
            for rate in self.rates:
                rate.curve = curve
                rate.pk = None
                rate.save()
        
    def load(self):
        try:
            curve = InterestRateCurve.objects.get(ccy=self.ccy, 
                                                  index=self.index,
                                                  term=self.term, 
                                                  numTerms=self.numTerms,
                                                  pricingDate=self.pricingDate, 
                                                  marketId=self.marketId)
        except InterestRateCurve.DoesNotExist:
            raise ErrorHandling.MarketDataMissing(str(self)+' cannot be loaded')

        #set the current curve to have the correct key
        self.id = curve.id
        self.loadRates()

    def loadRates(self):
        self.rates = []
        for rate in self.interestrate_set.all():
            self.addRate(rate)
#    @log
#    def saveRates(self):
#        '''
#        delete all rates in DB of the curve and then add all the rates to DB
#        ''' 
#        allRates = self.interestrate_set.all()
#        print '*'
#        print allRates
#        for rate in allRates:
#            rate.delete()
#        for rate in self.rates:
#            print '**'
#            print rate
#            rate.curve = self
#            self.interestrate_set.add(rate)
#            super(InterestRateCurve, self).save()
#            rate.save()
            
    def createShiftCurve(self, irCurve):
        #assume that both curves have same points
        shiftCurve = Shift.ShiftCurve()
        shiftCurve.shiftType = Enum.ShiftType('percentage')
        r = 0
        for rate in self.rates:
            shiftRate = InterestRate()
            shiftRate.type = rate.type
            shiftRate.term = rate.term
            shiftRate.numTerms = rate.numTerms
            shiftRate.mid = (irCurve.rates[r].mid-rate.mid)/rate.mid
            shiftCurve.shifts.append(shiftRate)
            r = r + 1
        return shiftCurve
    def shift(self, shiftAmount):
        for rate in self.rates:
            #print rate.mid
            rate.mid = rate.mid + shiftAmount
            #print rate.mid
        
    def adjustWithShiftCurve(self, shiftCurve):
        #assumes that shift curve has the same points as curve
        r = 0
        for rate in self.rates:
            #TODO: Fix to shift ir rate with correct rate from shiftcurve
            rate.mid = rate.mid * (1+shiftCurve.shifts[r].mid)
            r = r + 1
    def loadDefault(self, pricingDate):
        self.ccy = 'USD'
        self.index = Index('LIBOR')
        self.term = 'M'
        self.numTerms = 3
        self.pricingDate = Date.Date(month=9,day=12,year=2011)
        self.marketId = ''
        rate1 = InterestRate()
        rate1.type = 'Deposit'
        rate1.term = 'Y'
        rate1.numTerms = 1
        rate1.mid = 0.01
        rate1.curve = self
        self.rates = []
        self.rates.append(rate1)
        rate2 = InterestRate()
        rate2.type = 'Deposit'
        rate2.term = 'Y'
        rate2.numTerms = 30
        rate2.mid = 0.01
        rate2.curve = self
        self.rates.append(rate2)
    def printCurve(self):
        for rate in self.rates:
            print str(rate)

    def keysMatch(self, item):
        if item.pricingDate == self.pricingDate:
            if item.marketId == self.marketId:
                if item.ccy == self.ccy:
                    if item.index == self.index:
                        if item.term == self.term:
                            if item.numTerms == self.numTerms:
                                return True
        return False

    def addRate(self, rate):
        rate.curve = self
        exists = False
        for r in self.rates:
            if r.type == rate.type:
                if r.term == rate.term:
                    if r.numTerms == rate.numTerms:
                        exists = True
                        continue
        if exists == False:
            self.rates.append(rate)

    def buildZeroCurve(self):
        '''Build zero curve and returns QuantLib YieldTermStructure from 
        QuantLib. Uses QuantLib extensively
        '''
        # Map curve to QuantLib deposit and swap rates
        qlDeposits = {}
        qlSwaps = {}
        for rate in self.rates:
            if rate.type == 'Deposit':
                qlDeposits[rate.numTerms, rate.term.ql()] = rate.mid
            elif rate.type == 'Swap':
                qlSwaps[rate.numTerms, rate.term.ql()] = rate.mid
            else:
                raise ErrorHandling.OtherException('Bad rate type passed')
                
        # Build QL discount factor curve
        # convert them to Quote objects
        for n,unit in qlDeposits.keys():
            qlDeposits[(n,unit)] = QuantLib.SimpleQuote(qlDeposits[(n,unit)])
        for n,unit in qlSwaps.keys():
            qlSwaps[(n,unit)] = QuantLib.SimpleQuote(qlSwaps[(n,unit)])
            
        dayCounter = QuantLib.Actual360()
        settlementDays = 2
        depositHelpers = \
            [QuantLib.DepositRateHelper(QuantLib.QuoteHandle(qlDeposits[(n,unit)]),
                                        QuantLib.Period(n,unit), 
                                        settlementDays,
                                        QuantLib.TARGET(), 
                                        Enum.Roll('MF').ql(),
                                        False, dayCounter) \
            for n, unit in qlDeposits.keys()]
        
        fixedLegFrequency = Enum.Frequency('S').ql()
        fixedLegAdjustment = Enum.Roll('MF').ql()
        fixedLegDayCounter = QuantLib.Thirty360()
        swapHelpers = [ QuantLib.SwapRateHelper(QuantLib.QuoteHandle(qlSwaps[(n,unit)]),
                                       QuantLib.Period(n,unit), QuantLib.TARGET(),
                                       fixedLegFrequency, fixedLegAdjustment,
                                       fixedLegDayCounter, QuantLib.Euribor6M())
                        for n, unit in qlSwaps.keys() ]

        helpers = depositHelpers + swapHelpers
 
        return QuantLib.PiecewiseFlatForward(self.pricingDate.ql(), helpers, dayCounter)
#        return QuantLib.FlatForward(self.pricingDate.ql(), helpers, dayCounter)

class StockPrice(models.Model, cmt.cmt):
    equity = models.ForeignKey(Equity)
    pricingDate = modelFields.DateField()
    marketId = models.CharField(max_length=20, blank=True, default='')
    mid = models.FloatField()
    class Meta:
        db_table = 'cmt_stockprice'
        unique_together = ('equity', 'pricingDate', 'marketId')
    def __unicode__(self):
        return "%s/%s/%s" % (self.equity, self.pricingDate, self.marketId)
    def __str__(self):
        return "%s/%s/%s/%s" % (self.equity, self.pricingDate, self.marketId, self.mid)
    def save(self):
        try:
            stockPrice = StockPrice.objects.get(equity=self.equity, 
                                                pricingDate=self.pricingDate, 
                                                marketId=self.marketId)
            stockPrice.mid = self.mid
            super(StockPrice, stockPrice).save()
        except StockPrice.DoesNotExist:
            super(StockPrice, self).save()

        
    def createShiftCurve(self, stockPrice):
        shiftCurve = Shift.ShiftCurve()
        shiftCurve.shiftType = Enum.ShiftType('percentage')
        shiftCurve.shifts.append((self.pricingDate, (self.mid-stockPrice.mid)/stockPrice.mid))
        return shiftCurve
    
    def adjustWithShiftCurve(self, shiftCurve):
        self.mid = self.mid * (1+shiftCurve.shifts[0][1])

    def keysMatch(self, item):
        if item.pricingDate == self.pricingDate:
            if item.marketId == self.marketId:
                if item.equity.ticker == self.equity.ticker:
                    return True
        return False

class BondPrice(models.Model, cmt.cmt):
    '''
    Bond price is only used to imply the OAS. OAS is used for all P&L
    '''
    tCBond = models.ForeignKey(TCBond)
    pricingDate = modelFields.DateField()
    marketId = models.CharField(max_length=20, blank=True, default='')
    mid = models.FloatField()
    class Meta:
        db_table = 'cmt_bondprice'
        unique_together = ('tCBond', 'pricingDate', 'marketId')
    def __unicode__(self):
        return "%s/%s/%s" % (self.tCBond, self.pricingDate, self.marketId)
    def __str__(self):
        return "%s/%s/%s/%s" % (self.tCBond, self.pricingDate, self.marketId, self.mid)
    def save(self):
        try:
            bondPrice = BondPrice.objects.get(tCBond=self.tCBond, 
                                                pricingDate=self.pricingDate, 
                                                marketId=self.marketId)
            bondPrice.mid = self.mid
            super(BondPrice, bondPrice).save()
        except BondPrice.DoesNotExist:
            super(BondPrice, self).save()
        
    def keysMatch(self, item):
        if item.pricingDate == self.pricingDate:
            if item.marketId == self.marketId:
                #TODO: Fix the hardcoding of keysMatch to require that I know what the key of the underlying is
                if item.tCBond.name == self.tCBond.name:
                    return True
        return False

class BondOAS(models.Model, cmt.cmt):
    '''
    Bond price is only used to imply the OAS. OAS is used for all P&L
    '''
    tCBond = models.ForeignKey(TCBond)
    pricingDate = modelFields.DateField()
    marketId = models.CharField(max_length=20, blank=True, default='')
    mid = models.FloatField()
    class Meta:
        db_table = 'cmt_bondoas'
        unique_together = ('tCBond', 'pricingDate', 'marketId')
    def __unicode__(self):
        return "%s/%s/%s" % (self.tCBond, self.pricingDate, self.marketId)
    def __str__(self):
        return "%s/%s/%s/%s" % (self.tCBond, self.pricingDate, self.marketId, self.mid)
    def save(self):
        try:
            bondOAS = BondOAS.objects.get(tCBond=self.tCBond, 
                                          pricingDate=self.pricingDate, 
                                          marketId=self.marketId)
            bondOAS.mid = self.mid
            super(BondOAS, bondOAS).save()
        except BondOAS.DoesNotExist:
            super(BondOAS, self).save()

    def createShiftCurve(self, bondOAS):
        shiftCurve = Shift.ShiftCurve()
        shiftCurve.shiftType = Enum.ShiftType('percentage')
        if bondOAS.mid == 0:
            shiftCurve.shifts.append((self.pricingDate, 0.0))
        else:
            shiftCurve.shifts.append((self.pricingDate, (self.mid-bondOAS.mid)/bondOAS.mid))
        return shiftCurve

    def adjustWithShiftCurve(self, shiftCurve):
        self.mid = self.mid * (1+shiftCurve.shifts[0][1])
        
    def keysMatch(self, item):
        if item.pricingDate == self.pricingDate:
            if item.marketId == self.marketId:
                #TODO: Fix the hardcoding of keysMatch to require that I know what the key of the underlying is
                if item.tCBond.name == self.tCBond.name:
                    return True
        return False

class Batch(models.Model, cmt.cmt):
    """ Specifies Location a process runs in 
    Location contains the pricing date
    """
    batchDate = modelFields.DateField()
    class Meta:
        db_table = 'cmt_batch'

def tickerExists(positionType, ticker):
    exists = False
    if positionType == PositionType('CASH'):
        if ticker == 'Cash':
            return True
    if positionType == PositionType('EQUITY'):
        exists = Equity.objects.filter(ticker=ticker)
    elif positionType == PositionType('BOND'):
        exists = TCBond.objects.get(name=ticker)
    elif positionType == PositionType('SWAP'):
        exists = TCSwap.objects.get(name=ticker)
    if exists:
        return True
    else:
        return False

class Allocation(models.Model, cmt.cmt):
    '''
    Defines one individual allocation
    '''
    assetType = modelFields.AssetTypeField(max_length=30)
    percent = models.FloatField()
    user = models.ForeignKey(User)
    class Meta:
        db_table = 'cmt_allocation'
    def __unicode__(self):
        return u"%s/%s" % (self.user, self.assetType)
        
def main():
    pass
        
if __name__ == "__main__":
    main() 
