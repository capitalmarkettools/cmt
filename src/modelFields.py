'''
Created on Jul 10, 2012

@author: Tim Glauner
'''
from django.db import models
from src.bo.Enum import Roll, Frequency, Currency, TimePeriod
from src.bo.Enum import BondIdentifierType, PositionType, Index
from src.bo.Enum import TransactionType, AssetType
from src.bo.static import Basis, Calendar
from src.bo import Date

class CalendarField(models.CharField):
    '''
    Field used in Models to be Calendar
    '''

    description = "Calendar field"
    
    def __init__(self, *args, **kwargs):
        super(CalendarField, self).__init__(choices=Calendar.Calendar.choices, 
                                              *args, **kwargs)
        #Statement is not needed any more. Not sure why it works now withoutit
        #becuase it cause the field from validating
        #self.validators = self.default_validators
        
    __metaclass__ = models.SubfieldBase

    #takes value from DB and returns the correct python object
    def to_python(self, value):
        if isinstance(value, Calendar.Calendar):
            return value
        if value is None or value == '':
            return value
        #TODO: catch exception and raise ValidationError for forms
        return Calendar.createCalendar(value)
    def get_prep_value(self, value):
        return value.DBString()

class RollField(models.CharField):
    '''
    Field used in Models to be Calendar
    '''

    description = "Roll field"

    def __init__(self, *args, **kwargs):
        super(RollField, self).__init__(choices=Roll.choices, 
                                          *args, **kwargs)
#        self.validators = self.default_validators
        
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, Roll):
            return value
        if value is None or value == '':
            return value
        #TODO: catch exception and raise ValidationError for forms
        return Roll(value)
    def get_prep_value(self, value):
        return value.value
    
class FrequencyField(models.CharField):
    ''' Field used in Models to be Calendar '''

    description = "Frequency field"

    def __init__(self, *args, **kwargs):
        super(FrequencyField, self).__init__(choices=Frequency.choices,
                                               *args, **kwargs)
#        self.validators = self.default_validators
        
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, Frequency):
            return value
        if value is None or value == '':
            return value
        #TODO: catch exception and raise ValidationError for forms
        return Frequency(value)
    def get_prep_value(self, value):
        return value.value

class TimePeriodField(models.CharField):
    ''' Field used in Models to be Time Period from QuantLib '''

    description = "TimePeriod field"
    
    def __init__(self, *args, **kwargs):
        super(TimePeriodField, self).__init__(choices=TimePeriod.choices,
                                                *args, **kwargs)
 #       self.validators = self.default_validators
        
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, TimePeriod) or value is None or value == '':
            return value
        #TODO: catch exception and raise ValidationError for forms
        return TimePeriod(value)
    def get_prep_value(self, value):
        return value.value

class CurrencyField(models.CharField):
    '''
    Field used in Models to be Currency
    '''

    description = "Currency field"

    def __init__(self, *args, **kwargs):
        super(CurrencyField, self).__init__(choices=Currency.choices, *args, **kwargs)
        
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, Currency):
            return value
        if value is None or value == '':
            return value
        #TODO: catch exception and raise ValidationError for forms
        return Currency(value)
    def get_prep_value(self, value):
        return value.value

class IndexField(models.CharField):
    '''
    Field used in Models to be Index
    '''

    description = "Index field"

    def __init__(self, *args, **kwargs):
        super(IndexField, self).__init__(choices=Index.choices, *args, **kwargs)
        
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, Index):
            return value
        if value is None or value == '':
            return value
        #TODO: catch exception and raise ValidationError for forms
        return Index(value)
    def get_prep_value(self, value):
        return value.value

class BasisField(models.CharField):
    '''
    Field used in Models to be Basis
    '''

    description = "Frequency field"

    def __init__(self, *args, **kwargs):
        super(BasisField, self).__init__(choices=Basis.Basis.choices, *args, **kwargs)
        
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, Basis.Basis):
            return value
        if value is None or value == '':
            return value
        #TODO: catch exception and raise ValidationError for forms
        return Basis.createBasis(value)
    def get_prep_value(self, value):
        return value.DBString()

class BondIdentifierTypeField(models.CharField):
    '''
    Field used in Models to be Bond Identifier Type    '''

    description = "BondIdentifierType field"

    def __init__(self, *args, **kwargs):
        super(BondIdentifierTypeField, self).__init__(choices=BondIdentifierType.choices, *args, **kwargs)
        
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, BondIdentifierType):
            return value
        if value is None or value == '':
            return value
        #TODO: catch exception and raise ValidationError for forms
        return BondIdentifierType(value)
    def get_prep_value(self, value):
        return value.value

class PositionTypeField(models.CharField):
    '''
    Field used in Models to be Position Type    '''

    description = "PositionType field"

    def __init__(self, *args, **kwargs):
        super(PositionTypeField, self).__init__(choices=PositionType.choices, *args, **kwargs)
        
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, PositionType):
            return value
        if value is None or value == '':
            return value
        #TODO: catch exception and raise ValidationError for forms
        return PositionType(value)
    def get_prep_value(self, value):
        return value.value

class AssetTypeField(models.CharField):
    '''
    Field used in Models to be Position Type    '''

    description = "AssetType field"

    def __init__(self, *args, **kwargs):
        super(AssetTypeField, self).__init__(choices=AssetType.choices, *args, **kwargs)
        
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, AssetType):
            return value
        if value is None or value == '':
            return value
        #TODO: catch exception and raise ValidationError for forms
        return AssetType(value)
    def get_prep_value(self, value):
        return value.value

class TransactionTypeField(models.CharField):
    '''
    Field used in Models to be Transaction Type    '''

    description = "Transaction Type field"

    def __init__(self, *args, **kwargs):
        super(TransactionTypeField, self).__init__(choices=TransactionType.choices, *args, **kwargs)
        
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        if isinstance(value, TransactionType):
            return value
        if value is None or value == '':
            return value
        #TODO: catch exception and raise ValidationError for forms
        return TransactionType(value)
    def get_prep_value(self, value):
        return value.value

class DateField(models.DateField):
    '''
    Field used in Models to be Date
    '''

    description = "Date field"

    def __init__(self, *args, **kwargs):
        super(DateField, self).__init__(*args, **kwargs)
        
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
#        print "value in to_python: " + str(value)
        if isinstance(value, Date.Date):
            return value
        if value is None:
            return value
        #TODO: catch exception and raise ValidationError for forms
        d = Date.Date()
        d.fromPythonDate(value)
 #       print 'returned Date: ' + str(d)
        return d
    def get_prep_value(self, value):
  #      print 'value in get_prep_value: ' + str(value)
        return value.toPythonDate()
