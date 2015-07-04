from QuantLib import *

class QuantLibTester():
    "To play with QuantLib routines"
    def __init__(self):
        self.cal = TARGET()
        self.pricingDate = Date(6,November, 2008)
    def priceBond(self):
        Settings.instance().evaluationDate = self.pricingDate
        settlementDate = Date(8,November,2008);

        # market quotes
        deposits = {(1,Days): 0.03,
                    (1,Weeks): 0.0382,
                    (1,Months): 0.0372,
                    (3,Months): 0.0363,
                    (6,Months): 0.0353,
                    (9,Months): 0.0348,
                    (1,Years): 0.0345 }
        
        swaps = {(2,Years): 0.037125,
                 (3,Years): 0.0398,
                 (5,Years): 0.0443,
                 (10,Years): 0.05165,
                 (15,Years): 0.055175 }

        # convert them to Quote objects
        print deposits.keys()
        for n,unit in deposits.keys():
            deposits[(n,unit)] = SimpleQuote(deposits[(n,unit)])
        for n,unit in swaps.keys():
            swaps[(n,unit)] = SimpleQuote(swaps[(n,unit)])

        # build rate helpers
        dayCounter = Actual360()
        settlementDays = 2
        depositHelpers = [ DepositRateHelper(QuoteHandle(deposits[(n,unit)]),
                                             Period(n,unit), settlementDays,
                                             self.cal, ModifiedFollowing,
                                             False, dayCounter)
                            for n, unit in deposits.keys()]

        settlementDays = 2
        fixedLegFrequency = Annual
        fixedLegTenor = Period(1,Years)
        fixedLegAdjustment = Unadjusted
        fixedLegDayCounter = Thirty360()
        floatingLegFrequency = Semiannual
        floatingLegTenor = Period(6,Months)
        floatingLegAdjustment = ModifiedFollowing
        swapHelpers = [ SwapRateHelper(QuoteHandle(swaps[(n,unit)]),
                                       Period(n,unit), self.cal,
                                       fixedLegFrequency, fixedLegAdjustment,
                                       fixedLegDayCounter, Euribor6M())
                        for n, unit in swaps.keys() ]

       # term-structure construction

        helpers = depositHelpers + swapHelpers
        print depositHelpers
        print swapHelpers
        print helpers
        depoSwapCurve = PiecewiseFlatForward(settlementDate, helpers,
                                                    Actual360())

       #Pricing Engine
        discountTermStructure = RelinkableYieldTermStructureHandle()

        swapEngine = DiscountingSwapEngine(discountTermStructure)

       # Setup swap
        nominal = 1000000
        length = 5
        maturity = self.cal.advance(settlementDate,length,Years)
        payFixed = True

        fixedLegFrequency = Annual
        fixedLegAdjustment = Unadjusted
        fixedLegDayCounter = Thirty360()
        fixedRate = 0.04

        floatingLegFrequency = Semiannual
        spread = 0.0
        fixingDays = 2
        index = Euribor6M(discountTermStructure)
        floatingLegAdjustment = ModifiedFollowing
        floatingLegDayCounter = index.dayCounter()

        fixedSchedule = Schedule(settlementDate, maturity,
                                 fixedLegTenor, self.cal,
                                 fixedLegAdjustment, fixedLegAdjustment,
                                 DateGeneration.Forward, False)
        floatingSchedule = Schedule(settlementDate, maturity,
                                    floatingLegTenor, self.cal,
                                    floatingLegAdjustment, floatingLegAdjustment,
                                    DateGeneration.Forward, False)

        swap = VanillaSwap(VanillaSwap.Payer, nominal,
                           fixedSchedule, fixedRate, fixedLegDayCounter,
                           floatingSchedule, index, spread,
                           floatingLegDayCounter)
        
        swap.setPricingEngine(swapEngine)
        
        discountTermStructure.linkTo(depoSwapCurve)
        
        print "Swap = %.2f" % swap.NPV()
        print "Fair spread = %.6f" % swap.fairSpread()
        print "Fair rate = %.4f" % swap.fairRate()

        coupon = [0.04]
        
        bond = FixedRateBond(settlementDays, 100, fixedSchedule, coupon, 
                             Thirty360(), Unadjusted, 100, self.pricingDate)
        
        bondEngine = DiscountingBondEngine(discountTermStructure)
        bond.setPricingEngine(bondEngine)
        print "Bond Price = %.2f" % bond.cleanPrice()
        
        #shift curves and reprice bond
          # convert them to Quote objects
        for n,unit in deposits.keys():
            v = deposits[(n,unit)].value()
            deposits[(n,unit)].setValue(v+0.0001)
        for n,unit in swaps.keys():
            v = swaps[(n,unit)].value()
            swaps[(n,unit)].setValue(v+0.0001)

        # build rate helpers
        dayCounter = Actual360()
        settlementDays = 2
        depositHelpers = [ DepositRateHelper(QuoteHandle(deposits[(n,unit)]),
                                             Period(n,unit), settlementDays,
                                             self.cal, ModifiedFollowing,
                                             False, dayCounter)
                            for n, unit in deposits.keys()]

        settlementDays = 2
        fixedLegFrequency = Annual
        fixedLegTenor = Period(1,Years)
        fixedLegAdjustment = Unadjusted
        fixedLegDayCounter = Thirty360()
        floatingLegFrequency = Semiannual
        floatingLegTenor = Period(6,Months)
        floatingLegAdjustment = ModifiedFollowing
        swapHelpers = [ SwapRateHelper(QuoteHandle(swaps[(n,unit)]),
                                       Period(n,unit), self.cal,
                                       fixedLegFrequency, fixedLegAdjustment,
                                       fixedLegDayCounter, Euribor6M())
                        for n, unit in swaps.keys() ]

       # term-structure construction

        helpers = depositHelpers + swapHelpers
        depoSwapCurve = PiecewiseFlatForward(settlementDate, helpers,
                                                    Actual360())
        
        discountTermStructure.linkTo(depoSwapCurve)
        
        print "Shifted Swap = %.2f" % swap.NPV()
        print "Fair spread = %.6f" % swap.fairSpread()
        print "Fair rate = %.4f" % swap.fairRate()
        print "Shifted Bond = %.2f" % bond.NPV()

def main():
    t = QuantLibTester()
    t.priceBond()
if __name__ == "__main__":
    main()