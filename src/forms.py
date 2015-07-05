from django import forms
from src.bo.Enum import TimePeriod, Index, TransactionType, PositionType
from src.bo.static.Calendar import Calendar
import models
from models import Portfolio, TCBond, Identifier, Equity, ModelPosition, TCSwap
from models import InterestRateCurve, Location, UserProfile, Transaction, Batch
from ajax_select.fields import AutoCompleteSelectField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div

class HVaRParameters(forms.Form):
    def __init__(self, user, *args, **kwargs):
        #user is used in form validation. Can be changed at some point to request or session
        self.user = user
        super(HVaRParameters, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        
    portfolio = AutoCompleteSelectField('portfolio',required=True)
    startDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required = True)
    endDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    stepSize = forms.IntegerField(required=True)
    stepUnit = forms.ChoiceField(choices=TimePeriod.choices,required=True)
    calendar = forms.ChoiceField(choices=Calendar.choices,required=True)
    confLevel = forms.FloatField(required=True)
    pricingDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    marketId = forms.CharField(required=True)
    
    def clean(self):
        try:
            #TODO Maybe fix portfolio validation. Currently workaround used
            #only done to validate the field
            portfolio = self.cleaned_data['portfolio']
        except KeyError:
            raise forms.ValidationError('Some field does not exist')
        if self.cleaned_data['endDate'] <= self.cleaned_data['startDate']:
            raise forms.ValidationError('Start date must be before end date')
        return self.cleaned_data

class HVaRParametersPreConfigured(forms.Form):
    def __init__(self, user, *args, **kwargs):
        #user is used in form valiadtion. Can be changed at some point to request or session
        self.user = user
        super(HVaRParametersPreConfigured, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        
    portfolio = AutoCompleteSelectField('portfolio',required=True)
    config = AutoCompleteSelectField('hvarconfig',required=True)
    pricingDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    
    def clean(self):
        try:
            portfolio = self.cleaned_data['portfolio']
            config = self.cleaned_data['config']
        except KeyError:
            raise forms.ValidationError('Some field does not exist')
        return self.cleaned_data
        
class ValuationReportParameters(forms.Form):
    def __init__(self, user, *args, **kwargs):
        #user is used in form validation. Can be changed at some point to request or session
        self.user = user
        super(ValuationReportParameters, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        
    portfolio = AutoCompleteSelectField('portfolio',required=True)
    pricingDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    marketId = forms.CharField(required=True)
    
    def clean(self):
        try:
            portfolio = self.cleaned_data['portfolio']
        except KeyError:
            raise forms.ValidationError('Portfolio does not exist')
        return self.cleaned_data

class LoadEquityPrices(forms.Form):
    def __init__(self, *args, **kwargs):
        super(LoadEquityPrices, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        
    equity = AutoCompleteSelectField('equity')
    startDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    endDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    calendar = forms.ChoiceField(choices=Calendar.choices,required=True)
    marketId = forms.CharField(required=True)
    
    def clean(self):
        if self.cleaned_data['endDate'] < self.cleaned_data['startDate']:
            raise forms.ValidationError('Start date must be equal or before end date')
        return self.cleaned_data

class LoadMissingMarketDataForPortfolioForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(LoadMissingMarketDataForPortfolioForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

    portfolio = AutoCompleteSelectField('portfolio',required=True)
    asOf = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    startDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    endDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    calendar = forms.ChoiceField(choices=Calendar.choices,required=True)
    marketId = forms.CharField(required=True)
    
    def clean(self):
        if self.cleaned_data['endDate'] < self.cleaned_data['startDate']:
            raise forms.ValidationError('Start date must be equal or before end date')
        return self.cleaned_data
    
class PositionReportParameters(forms.Form):
    def __init__(self, user, *args, **kwargs):
        #user is used in form valiadtion. Can be changed at some point to request or session
        self.user = user
        super(PositionReportParameters, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        
    portfolio = AutoCompleteSelectField('portfolio')
    pricingDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
       
    def clean(self):
        try:
            portfolio = self.cleaned_data['portfolio']
        except KeyError:
            raise forms.ValidationError('Portfolio does not exist')
        return self.cleaned_data
    
class EquityPricesReportForm(forms.Form):
    equity = AutoCompleteSelectField('equity', required=True)
    marketId = forms.CharField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(EquityPricesReportForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
    def clean(self):
        try:
            equity = self.cleaned_data['equity']
        except KeyError:
            raise forms.ValidationError('Equity does not exist')
        return self.cleaned_data

class PortfolioForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(PortfolioForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        
    class Meta:
        model = Portfolio

    def clean(self):
        formInputUser = self.cleaned_data['user']
        if not self.user.username == formInputUser:
            raise forms.ValidationError('Use your own user name as user')
        return self.cleaned_data
    
class TCBondCalculatorForm(forms.ModelForm):
    pricingDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'), 
                                  input_formats=('%m/%d/%y',))
    marketId = forms.CharField()
    startDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'), 
                                input_formats=('%m/%d/%y',))
    endDate = forms.DateField(widget=forms.DateInput(format = '%m/%d/%y'), 
                                input_formats=('%m/%d/%y',))
    def __init__(self, *args, **kwargs):
        super(TCBondCalculatorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(Div(Div('pricingDate', 'name', 'startDate', 'coupon', 'paymentFrequency', 'paymentCalendar',
                                            css_class='large-6 columns'),
                                        Div('marketId', 'ccy', 'endDate', 'basis', 'paymentRollRule', 'paymentCalendar',
                                            css_class='large-6 columns'),
                                        css_class="row"))
    class Meta:
        model = TCBond
    def clean(self):
        return self.cleaned_data

class TCSwapCalculatorForm(forms.ModelForm):
    pricingDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'), 
                                  input_formats=('%m/%d/%y',))
    marketId = forms.CharField()
    
    startDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'), 
                                input_formats=('%m/%d/%y',))
    endDate = forms.DateField(widget=forms.DateInput(format = '%m/%d/%y'), 
                                input_formats=('%m/%d/%y',))
    
    def __init__(self, *args, **kwargs):
        super(TCSwapCalculatorForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(Div(Div('pricingDate', 'name', 'startDate',
                                            css_class='large-6 columns'),
                                        Div('marketId', 'ccy', 'endDate',
                                            css_class='large-6 columns'),
                                        css_class="row"),
                                    Div(Div('fixedCoupon','fixedBasis', 'fixedPaymentFrequency', 
                                            'fixedPaymentRollRule', 'fixedPaymentCalendar', 
                                            css_class="large-6 columns"),
                                        Div('floatingIndex','floatingIndexTerm', 'floatingIndexNumTerms', 'floatingSpread',
                                            'floatingBasis', 'floatingPaymentFrequency', 'floatingPaymentRollRule',
                                            'floatingPaymentCalendar', 'floatingResetFrequency', 'floatingResetRollRule',
                                            'floatingResetCalendar', 
                                            css_class="large-6 columns"),
                                        css_class="row"))        
    class Meta:
        model = TCSwap
    def clean(self):
        if self.cleaned_data['floatingIndex'] <> Index('LIBOR'):
            raise forms.ValidationError('Only Libor currently implemented')
        return self.cleaned_data

class IdentifierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(IdentifierForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        model = Identifier
    def clean(self):
        return self.cleaned_data

class EquityForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EquityForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
    class Meta:
        model = Equity
    def clean(self):
        return self.cleaned_data

class PositionForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(PositionForm, self).__init__(*args, **kwargs)
        self.fields['portfolio'].queryset = Portfolio.objects.filter(user=user)
        self.helper = FormHelper()
        
    class Meta:
        model = ModelPosition
    def clean(self):
        positionType = self.cleaned_data['positionType']
        ticker = self.cleaned_data['ticker']
        if positionType not in tuple(x[0] for x in PositionType.choices):
            raise forms.ValidationError('PositionType %s invalid' % positionType)
        if not models.tickerExists(positionType, ticker):
            raise forms.ValidationError('Ticker %s does not exist' % ticker)
        return self.cleaned_data
    
class InterestRateCurveReportParameters(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        #user is used in form valiadtion. Can be changed at some point to request or session
        super(InterestRateCurveReportParameters, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        model = InterestRateCurve
    def clean(self):
        term = self.cleaned_data['term']
        return self.cleaned_data

class CorrelationReportParameters(forms.Form):
    def __init__(self, user, *args, **kwargs):
        #user is used in form valiadtion. Can be changed at some point to request or session
        self.user = user
        super(CorrelationReportParameters, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

    portfolio = AutoCompleteSelectField('portfolio', required=True)
    benchmark = AutoCompleteSelectField('equity', required=True)
    startDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    endDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    stepSize = forms.IntegerField(required=True)
    stepUnit = forms.ChoiceField(choices=TimePeriod.choices, required=True)
    calendar = forms.ChoiceField(choices=Calendar.choices, required=True)
    pricingDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    marketId = forms.CharField(required=True)
    
    def clean(self):
        #TODO LOW Change the validation on the form to a form portfolio field
        try:
            portfolio = self.cleaned_data['portfolio']
            benchmark = self.cleaned_data['benchmark']
        except KeyError:
            raise forms.ValidationError('One Field does not exist')
        return self.cleaned_data

class LocationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LocationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
    class Meta:
        model = Location
    def clean(self):
        return self.cleaned_data

class UserProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
    class Meta:
        model = UserProfile
    def clean(self):
        return self.cleaned_data

class TCBondForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TCBondForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
    class Meta:
        model = TCBond

    def clean(self):
        return self.cleaned_data

class TCSwapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TCSwapForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
    class Meta:
        model = TCSwap
    def clean(self):
        if self.cleaned_data['floatingIndex'] <> Index('LIBOR'):
            raise forms.ValidationError('Only Libor currently implemented')
        return self.cleaned_data

class TransactionForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)
        self.fields['portfolio'].queryset = Portfolio.objects.filter(user=user)
        self.helper = FormHelper()

    class Meta:
        model = Transaction
        exclude = ('reflectedInPosition')
    def clean(self):
        transactionType = self.cleaned_data['transactionType']
        if transactionType not in tuple(x[0] for x in TransactionType.choices):
            raise forms.ValidationError('TransactionType %s not valid' % transactionType)
        positionType = self.cleaned_data['positionType']
        if positionType not in tuple(x[0] for x in PositionType.choices):
            raise forms.ValidationError('PositionType %s invalid' % positionType)
        ticker = self.cleaned_data['ticker']
        if not models.tickerExists(positionType, ticker):
            raise forms.ValidationError('Ticker %s does not exist' % ticker)
        return self.cleaned_data

class BatchForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BatchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
    class Meta:
        model = Batch

class MultiBatchesForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(MultiBatchesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

    startDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    endDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)

class PerformanceReportParameters(forms.Form):
    def __init__(self, user, *args, **kwargs):
        #user is used in form valiadtion. Can be changed at some point to request or session
        self.user = user
        super(PerformanceReportParameters, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        
    startDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    endDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    marketId = forms.CharField(required=True)
       
    def clean(self):
        if self.cleaned_data['endDate'] == self.cleaned_data['startDate']:
            raise forms.ValidationError('Start date cannot be equal to end date')
        return self.cleaned_data

class AssetAllocationReportParameters(forms.Form):
    def __init__(self, user, *args, **kwargs):
        #user is used in form valiadtion. Can be changed at some point to request or session
        self.user = user
        super(AssetAllocationReportParameters, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        
    pricingDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    marketId = forms.CharField(required=True)
       
    def clean(self):
        return self.cleaned_data

class NetWorthTrendReportParameters(forms.Form):
    def __init__(self, user, *args, **kwargs):
        #user is used in form valiadtion. Can be changed at some point to request or session
        self.user = user
        super(NetWorthTrendReportParameters, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        
    startDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    endDate = forms.DateField(widget = forms.DateInput(format = '%m/%d/%y'),input_formats = ('%m/%d/%y',),required=True)
    marketId = forms.CharField(required=True)
       
    def clean(self):
        if self.cleaned_data['endDate'] == self.cleaned_data['startDate']:
            raise forms.ValidationError('Start date cannot be equal to end date')
        return self.cleaned_data
