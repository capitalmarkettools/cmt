'''
Created on Nov 11, 2009

@author: capitalmarkettools
'''
import QuantLib
from src.bo import cmt, ErrorHandling

#TODO: Introduce EnumQuantLib class that introduces ql() and qlMapping attributes
class Enum(cmt.cmt):
    qlMapping = {}
    name = ''
    def __init__(self, value=None):
        super(Enum, self).__init__()
        if value == None:
            raise ErrorHandling.OtherException('Enumeration requires value in constructor.')
        if value not in [element[0] for element in self.choices]:
            raise ErrorHandling.OtherException('Enumeration value %s not found for enumeration.' % value)
        self._value = value
    
    def set_value(self, value):
        self._value = value
    
    def get_value(self):
        return self._value
    
    def __eq__(self, value):
        return self._value == value
#        if isinstance(other, self.__class__):
#            return self.qlMapping[self._value] == other.qlMapping[other.value]
#        else:
#            return False
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __len__(self):
        return len(self._value)
    
    def __str__(self):
        return '%s' % (self._value)
    value = property(get_value, set_value)
    
    def __unicode__(self):
        return '%s' % (self._value)
    
class Roll(Enum):
    ''' 
    Roll convention when day falls onto non-business day
    '''
    qlMapping = {'F': QuantLib.Following,
               'MF': QuantLib.ModifiedFollowing,
               'P': QuantLib.Preceding,
               'MP': QuantLib.ModifiedPreceding,
               'U': QuantLib.Unadjusted,
               'JH': QuantLib.JoinHolidays,
               'JB': QuantLib.JoinBusinessDays,
    }
    choices = (('F','Following'),
               ('MF','Modified Following'),
               ('P','Preceding'),
               ('MP','Modified Preceding'),
               ('U','Unadjusted'),
               ('JH','Join Holidays'),
               ('JB','Join Business Days'),)
    
    name = 'Roll'
    def __init__(self, value=None):
        super(Roll, self).__init__(value)
    def ql(self):
        return self.qlMapping[self._value]

class Frequency(Enum):
    ''' 
    Frequency. Used for example for payment frequency
    '''
    qlMapping = {'N': QuantLib.NoFrequency,
               'O': QuantLib.Once,
               'A': QuantLib.Annual,
               'S': QuantLib.Semiannual,
               'EFM': QuantLib.EveryFourthMonth,
               'Q': QuantLib.Quarterly,
               'BM': QuantLib.Bimonthly,
               'M': QuantLib.Monthly,
               'EFW': QuantLib.EveryFourthWeek,
               'BW': QuantLib.Biweekly,
               'W': QuantLib.Weekly,
               'D': QuantLib.Daily,
    }
    choices = (('N','None'),
               ('O','Once'),
               ('A','Annual'),
               ('S','Semi Annual'),
               ('EFM','Every Fourth Month'),
               ('Q','Quarterly'),
               ('BM','Bi Monthly'),
               ('M','Monthly'),
               ('EFW','Every Four Weeks'),
               ('BW','Bi Weekly'),
               ('W','Weekly'),
               ('D','Daily'),)
    
    name = 'Frequency'
    def __init__(self, value=None):
        super(Frequency, self).__init__(value)
    def ql(self):
        return self.qlMapping[self._value]

class TimePeriod(Enum):
    ''' 
    Time period. Specify unit such as Days, Weeks...
    '''
    qlMapping = {'D': QuantLib.Days,
               'W': QuantLib.Weeks,
               'M': QuantLib.Months,
               'Y': QuantLib.Years,
    }
    choices = (('D','Days'),
               ('W','Weeks'),
               ('M','Months'),
               ('Y','Years'),)
    
    name = 'TimePeriod'
    def __init__(self, value=None):
        super(TimePeriod, self).__init__(value)
    def ql(self):
        return self.qlMapping[self._value]

class Currency(Enum):
    ''' 
    Stores enumeration as string
    '''
    qlMapping = {'USD': QuantLib.USDCurrency,
               'EUR': QuantLib.EURCurrency,
    }
    choices = (('USD','US Dollar'),
               ('EUR','Euro'),)
    name = 'Currency'
    def __init__(self, value=None):
        super(Currency, self).__init__(value)
    def ql(self):
        return self.qlMapping[self._value]

class Index(Enum):
    ''' 
    Stores enumeration as string
    '''
    qlMapping = {'LIBOR': 'Libor',
                 'OIS': 'OIS',
                 'PRIME': 'Prime',
                 'CP': 'Commercial Paper',
    }
    choices = (('LIBOR', 'Libor'),
               ('OIS', 'OIS'),
               ('PRIME', 'Prime'),
               ('CP', 'Commercial Paper'),)
    name = 'Index'
    def __init__(self, value=None):
        super(Index, self).__init__(value)
    def ql(self):
        return self.qlMapping[self._value]

class BondIdentifierType(Enum):
    ''' 
    Stores enumeration as string
    '''
    #TODO Why do we need this qlMapping?
#    qlMapping = {'CUSIP':'CUSIP',
 #              'ISIN':'ISIN',
  #             'BLOOMBERG':'BLOOMBERG',
   # }
    choices = (('CUSIP','Cusip'),
               ('ISIN','Isin'),
               ('BLOOMBERG','Bloomberg'),)
    name = 'BondIdentifierType'
    def __init__(self, value=None):
        super(BondIdentifierType, self).__init__(value)

class PositionType(Enum):
    ''' 
    Stores enumeration as string
    '''
    choices = (('CASH','Cash'),
               ('EQUITY','Equity'),
               ('BOND','Bond'),
               ('SWAP','Swap'),)
    name = 'PositionType'
    def __init__(self, value=None):
        super(PositionType, self).__init__(value)

class AssetType(Enum):
    ''' 
    Stores enumeration as string
    '''
    choices = (('CASH','Cash'),
               ('EQUITYUS','Equity US'),
               ('EQUITYDEV','Equity Developed Markets'),
               ('EQUITYEM','Equity Emerging Markets'),
               ('REIT','Reit'),
               ('SOVBOND','Sovereign Bond'),
               ('NYMUNIBOND','NY Muni Bond'),
               ('CORPBOND','Corp Bond'),
               ('OTHERBOND','Other Bond'),
               ('BONDFUND','Bond Fund'),
               ('EQUITYSMALLCAPUS','Small Cap US Equity'),
               ('COMMODITY','Commodity'),
               ('EQUITYPREF','Preferred Equity'),
               ('IRSWAP','Interest Rate Swap'),
               ('OTHER','Other'),
               ('GOLD','Gold'),)
    
    name = 'AssetType'
    def __init__(self, value=None):
        super(AssetType, self).__init__(value)

class TransactionType(Enum):
    ''' 
    Stores enumeration as string
    '''
    choices = (('BUY','Buy'),
               ('SELL','Sell'),
               ('DIVIDEND','Dividend'),
               ('COUPON','Coupon'),
               ('ADD','Add'),
               ('REMOVE','Remove'),
               ('INIT','Init'),)
    name = 'TransactionType'
    def __init__(self, value=None):
        super(TransactionType, self).__init__(value)


#class TermUnit(object):
#    """DAYS, WEEKS, MONTHS, YEARS
#    """
#    def __init__(self, name):
#        self.name = name
#    def __str__(self):
#       return self.name
#    def __repr__(self):
#       return '<TermUnit: %s>' % self
#TermUnit.DAYS = TermUnit('days')
#TermUnit.WEEKS = TermUnit('weeks')
#TermUnit.MONTHS = TermUnit('months')
#TermUnit.YEARS = TermUnit('years')
       
Sunday = QuantLib.Sunday
Monday = QuantLib.Monday
Tuesday = QuantLib.Tuesday
Wednesday = QuantLib.Wednesday
Thursday = QuantLib.Thursday
Friday = QuantLib.Friday
Saturday = QuantLib.Saturday

January = QuantLib.January
February = QuantLib.February
March = QuantLib.March
April = QuantLib.April
May = QuantLib.May
June = QuantLib.June
July = QuantLib.July
August = QuantLib.August
September = QuantLib.September
October = QuantLib.October
November = QuantLib.November
December = QuantLib.December

class ShiftType(cmt.cmt):
    """Enumeration to define shift type
    ABSOLUTE, PERCENTAGE
    """
    def __init__(self, name):
        self.name = name
    
ShiftType.ABSOLUTE = ShiftType('absolute')
ShiftType.PERCENTAGE = ShiftType('percentage')

def main():
    print 'Start'
    print ShiftType.ABSOLUTE
    print ShiftType.PERCENTAGE
#    print TermUnit.DAYS
#    print TermUnit.WEEKS
#    print TermUnit.MONTHS
#    print TermUnit.YEARS
    r = Roll('F')
    print r
    print r.ql()
    import json
    print json.dumps(r)
    print 'End'     
if __name__ == "__main__":
    main() 
