'''
Created on Oct 22, 2009

@author: capitalmarkettools
'''
import unittest
from src.bo.tests import EquityPositionTest
from src.bo.tests import BondPositionTest
from src.bo.tests import SwapPositionTest
from src.bo.tests import DateTest
from src.bo.tests import HistoricalVARTest
from src.bo.tests import PortfolioTest
from src.bo.tests import VARUtilitiesTest
from src.bo.tests import CalendarTest
from src.bo.tests import StockPriceTest
from src.bo.tests import ShiftTest
from src.bo.tests import EnumTest
from src.bo.tests import MarketDataContainerTest
from src.bo.tests import MarketDataScenarioTest
from src.bo.tests import PositionTest
from src.bo.tests import InterestRateCurveTest
from src.bo.tests import ImplyOASTest
from src.bo.tests import BondOASTest
from src.bo.tests import TimeSeriesNPVCalculatorTest

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    allTests = unittest.TestSuite([EquityPositionTest.suite(), 
                                   BondPositionTest.suite(), 
                                   SwapPositionTest.suite(), 
                                   DateTest.suite(), 
                                   HistoricalVARTest.suite(),
                                   PortfolioTest.suite(),
                                   VARUtilitiesTest.suite(),
                                   CalendarTest.suite(),
                                   StockPriceTest.suite(),
                                   ShiftTest.suite(),
                                   EnumTest.suite(),
                                   MarketDataContainerTest.suite(),
                                   PositionTest.suite(),
                                   MarketDataScenarioTest.suite(),
                                   ImplyOASTest.suite(),
                                   BondOASTest.suite(),
                                   TimeSeriesNPVCalculatorTest.suite(),
                                   InterestRateCurveTest.suite()])
    runner.run(allTests)