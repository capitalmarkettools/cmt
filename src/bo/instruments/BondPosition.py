'''
Created on Feb 2, 2010

@author: capitalmarkettools
'''
import QuantLib
from src.bo.instruments import Position
from src.bo.static import Basis
from src.bo import ErrorHandling, Date, Enum
from src.bo import MarketDataContainer
from src.bo.decorators import log
from src.models import InterestRateCurve, TCBond, BondOAS

@log
class BondPosition(Position.Position):
    '''
    BondPosition consists of amount and secId. The underlying tc for bond
    is loaded from the DB or if tCBond is given then tCBond is used
    '''
    def __init__(self, amount = None, secId = None, tCBond = None):
        if amount == None:
            raise ErrorHandling.OtherException('amount must be given for BondPosition')
        if secId == None and tCBond == None:
            raise ErrorHandling.OtherException('either secId or tCBond need to be given')
        Position.Position.__init__(self, 'BondPosition', amount, secId)
        if tCBond == None:
            self.tCBond = TCBond.objects.get(name=secId)
        else:
            self.tCBond = tCBond
        #Used for caching to see if qlSetup() needs to be called again
        self.qlBond = None
        self.pricingDate = None
        
    def __str__(self):
        return '<%s,%s,%d>' % (self.__class__, self.secId, self.amount)
    
    def marketData(self, pricingDate, marketId=''):
        irCurve = InterestRateCurve()
        irCurve.ccy = self.tCBond.ccy
        irCurve.index = Enum.Index('LIBOR')
        irCurve.term = 'M'
        irCurve.numTerms = 3
        irCurve.pricingDate = pricingDate
        irCurve.marketId = marketId
        irCurve.load()
        l = []
        l.append(irCurve)
        ##print pricingDate
        bondOAS = BondOAS.objects.get(tCBond=self.tCBond, pricingDate=pricingDate,
                                      marketId=marketId)
        l.append(bondOAS)
        return l
    
    def loadAndSaveMarketData(self, pricingDate, marketId):
        ''' assumes that 'EOD' marketId exists '''
        eodCurve = InterestRateCurve()
        eodCurve.ccy = self.tCBond.ccy
        eodCurve.index = Enum.Index('LIBOR')
        eodCurve.term = 'M'
        eodCurve.numTerms = 3
        eodCurve.pricingDate = pricingDate
        eodCurve.marketId = 'EOD'
        eodCurve.load()
        irCurve = InterestRateCurve()
        irCurve.ccy = self.tCBond.ccy
        irCurve.index = Enum.Index('LIBOR')
        irCurve.term = 'M'
        irCurve.numTerms = 3
        irCurve.pricingDate = pricingDate
        irCurve.marketId = marketId
        eodRates = eodCurve.getRates()
        for rate in eodRates:
            irCurve.addRate(rate)
        irCurve.save()
        eodBondOAS = BondOAS.objects.get(tCBond=self.tCBond, pricingDate=pricingDate,
                                      marketId='EOD')
        bondOAS = BondOAS(tCBond=self.tCBond, pricingDate=pricingDate,
                          marketId=marketId,mid=eodBondOAS.mid)
        bondOAS.save()
        
    def setupQL(self, pricingDate, marketId=''):
        QuantLib.Settings.instance().evaluationDate = pricingDate.ql()
        # Get market data curve based on Ccy/Index
        self.pricingDate = pricingDate
        curve = InterestRateCurve()
        curve.pricingDate = pricingDate
        curve.ccy = self.tCBond.ccy
        #TODO Fix term to make it TimePeriod
        curve.index = Enum.Index('LIBOR')
        curve.term = 'M'
        curve.numTerms = 3
        curve.marketId = marketId
#        print 'marketDataContainer in setupQL'
 #       print self.marketDataContainer
        if self.marketDataContainer == None:
            raise ErrorHandling.MarketDataMissing('marketDataContainer is None')
        newCurve = self.marketDataContainer.find(curve)
        #print 'newCurve in setupQL'
        #print newCurve
        if newCurve == None:
            raise ErrorHandling.MarketDataMissing('Cannot find market data %s' % curve)
        #load OAS and adjust discount curve
        bondOAS = self.marketDataContainer.find(BondOAS(marketId=marketId,pricingDate=pricingDate,
                                                        tCBond=self.tCBond))
        newCurve.shift(shiftAmount=bondOAS.mid)
        # Map curve to QuantLib deposit rates
        depositCurve = newCurve.buildZeroCurve()
        #print 'deposit curve in setupQL'
        #print depositCurve.nodes()
        #Pricing Engine
        discountTermStructure = QuantLib.RelinkableYieldTermStructureHandle()
        discountTermStructure.linkTo(depositCurve)

        fixedSchedule = QuantLib.Schedule(pricingDate.ql(), 
                                          Date.createQLDateFromPythonDate(self.tCBond.endDate),
                                          QuantLib.Period(1,QuantLib.Years),
                                          self.tCBond.paymentCalendar.ql(),
                                          self.tCBond.paymentRollRule.ql(), 
                                          self.tCBond.paymentRollRule.ql(),
                                          QuantLib.DateGeneration.Forward, 
                                          False)
                
        coupons = []
        coupons.append(float(self.tCBond.coupon))
        #print self.tCBond.coupon
        #print self.tCBond.coupon.__class__
#        coupons.append(0.04)
        self.qlBond = QuantLib.FixedRateBond(2, 
                                      100, 
                                      fixedSchedule, 
                                      coupons, 
                                      self.tCBond.basis.ql(), 
                                      self.tCBond.paymentRollRule.ql(), 
                                      100, 
                                      pricingDate.ql())
        
        bondEngine = \
            QuantLib.DiscountingBondEngine(discountTermStructure)
        self.qlBond.setPricingEngine(bondEngine)
        self.upToDate = True
    
    def NPV(self, pricingDate, marketId=''):
        if self.qlBond == None or self.pricingDate <> pricingDate or self.upToDate == False:
            self.setupQL(pricingDate, marketId)
        return self.qlBond.cleanPrice() * float(self.amount)
    
    def PriceToYield(self, price, pricingDate, marketId):
        if self.qlBond == None or self.pricingDate <> pricingDate or self.upToDate == False:
            self.setupQL(pricingDate, marketId)
        return self.qlBond.bondYield(price, Basis.Thirty360().ql(), Enum.Frequency('S').ql(), 
                                     Enum.Frequency('S').ql())
        
    def YieldToPrice(self, bondYield, pricingDate, marketId):
        if self.qlBond == None or self.pricingDate <> pricingDate or self.upToDate == False:
            self.setupQL(pricingDate, marketId)
        return self.qlBond.cleanPrice(bondYield, Basis.Thirty360().ql(), Enum.Frequency('S').ql(), 
                                     Enum.Frequency('S').ql())
        
    def getAssetType(self):
        return self.tCBond.assetType
        
def main():
    pos = BondPosition(100, 'PortAuth_4.00_JAN42')
    pricingDate = Date.Date(month=8, day=20, year=2013)
    marketId = 'EOD'
    QuantLib.Settings.instance().evaluationDate = pricingDate.ql()
    marketDataContainer = MarketDataContainer.MarketDataContainer()
    marketDataContainer.add(pos.marketData(pricingDate, marketId))
    pos.setMarketDataContainer(marketDataContainer)
    print "Fair Price: " + str(pos.NPV(pricingDate, marketId))
    print "Yield: " + str(pos.PriceToYield(104.3562, pricingDate, marketId)*100) + "%"
    print "Yield to Price: " + str(pos.YieldToPrice(0.03, pricingDate, marketId))
    
if __name__ == "__main__":
    main()