import json
from QuantLib import Settings
from matplotlib.dates import YearLocator, MonthLocator
from scipy.stats.stats import pearsonr
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.simple import direct_to_template
from models import Portfolio, ModelPosition, HvarConfiguration, TCBond, Identifier
from models import StockPrice, Equity, InterestRateCurve, Batch
from models import  Location, UserProfile, TCSwap, Transaction, Allocation
from forms import HVaRParameters, LoadEquityPrices
from forms import PositionReportParameters, EquityPricesReportForm
from forms import ValuationReportParameters, PortfolioForm, TCBondForm
from forms import TCSwapForm, TCBondCalculatorForm, TCSwapCalculatorForm
from forms import IdentifierForm, HVaRParametersPreConfigured, EquityForm
from forms import PositionForm, InterestRateCurveReportParameters, MultiBatchesForm
from forms import CorrelationReportParameters, LocationForm, UserProfileForm
from forms import LoadMissingMarketDataForPortfolioForm, TransactionForm, BatchForm
from forms import PerformanceReportParameters, AssetAllocationReportParameters
from forms import NetWorthTrendReportParameters
from src.bo import VARUtilities, Enum, ErrorHandling
from src.bo.Date import Date, createPythonDateFromQLDate
from src.bo.instruments.BondPosition import BondPosition
from src.bo.instruments.SwapPosition import SwapPosition
from src.bo.instruments.FinancialInstrument import CreatePosition
from src.bo.HistoricalVAR import HistoricalVAR
from src.bo import MarketDataContainer
from src.bo.decorators import logShort
from src.bo.utilities.MarketDataLoader import EquityPriceLoader
from src.bo.utilities import Converter
from src.bo.static import Calendar
from src.bo.calculators.PerformanceCalculator import PerformanceCalculator
from src.bo.calculators.TimeSeriesNPVCalculator import TimeSeriesNPVCalculatorParameters, TimeSeriesNPVCalculator
import matplotlib.pyplot as plt
from matplotlib import ticker
from matplotlib.backends.backend_agg import FigureCanvasAgg 
from datetime import date
from misc.batch import BatchUtility
from collections import OrderedDict

@csrf_exempt
def home(request):
    return direct_to_template(request,'HistoricalVAR/home.html')

@csrf_exempt
def landingPage(request):
    return direct_to_template(request,'HistoricalVAR/landingPage/index.html')

@csrf_exempt
def altGUI(request):
    return direct_to_template(request,'HistoricalVAR/altGUI.html')

@login_required
@csrf_exempt
def logged_in(request):
    return direct_to_template(request,'HistoricalVAR/home.html')

@login_required
@csrf_exempt
def notYetImplemented(request):
    return direct_to_template(request,'HistoricalVAR/notYetImplemented.html',
                              {'title':'Not Implemented'})

@login_required
@csrf_exempt
def showEquityPrices(request):
    if request.method == 'POST':
        form = EquityPricesReportForm(request.POST)
        if form.is_valid():
            equity = form.cleaned_data['equity']
            marketId = form.cleaned_data['marketId']
            stockPrices = StockPrice.objects.filter(equity__ticker=equity.ticker, marketId=marketId)
            ret = [(str(p.pricingDate), p.marketId, p.equity.ticker, float(p.mid)) for p in stockPrices]          
            return direct_to_template(request,'HistoricalVAR/equityPrices.html',
                                      {'jsonEquityPrices':json.dumps(ret)})

        else:
            form = EquityPricesReportForm(request.POST)
    else:
        form = EquityPricesReportForm(initial={'marketId':request.user.get_profile().marketId})
 
    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html', 
                              {'form':form, 'title':'Equity Prices Report' })    

@login_required
@csrf_exempt
def showEquityPricesExcel(request):
    allEquityPrices = StockPrice.objects.all()
    response = direct_to_template(request,'HistoricalVAR/equityPricesToExcel.html',
                                  {'allEquityPrices':allEquityPrices})
    filename = "testFile.xls"
    response['Content-Disposition'] = 'attachment; filename=' + filename
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    return response
    
@login_required
@csrf_exempt
def googleChartAPITest(request):
    return direct_to_template(request,'HistoricalVAR/googleChartAPITest.html')

@login_required
@csrf_exempt
def chartTest(request):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.title("Title")
    plt.suptitle("Suptitle")
    plt.xlabel("Dates")
    #it actually supports TeX
    plt.ylabel("here " + r'is theta: $\theta$')
    #also supports annotate. figtext, text
    xdata, ydata = [date(2006, 1, 1), date(2007, 1, 1), date(2008, 1, 1),
                    date(2009, 1, 1), date(2010, 1, 1)], [2, 2, 1, 3, 4]
    ax.plot(xdata, ydata)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('$%1.2f'))
    [tick.label1.set_color('green') for tick in ax.xaxis.get_major_ticks()]
    fig.autofmt_xdate()
    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

@login_required
@csrf_exempt
def excelTest(request):
    testDate = [(1, 2), (3, 4)]
    response = direct_to_template(request,'HistoricalVAR/excelTest.html')
    filename = "testFile.xls"
    response['Content-Disposition'] = 'attachment; filename=' + filename
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    return response

@login_required
@csrf_exempt
@logShort
def hvarPortfolioWithParametersCalculate(request):
    if request.method == 'POST':
        form = HVaRParameters(data=request.POST, user=request.user)
        if form.is_valid():
            portfolio = form.cleaned_data['portfolio']
            startDate = Date()
            startDate.fromPythonDate(form.cleaned_data['startDate'])
            endDate = Date()
            endDate.fromPythonDate(form.cleaned_data['endDate'])
            stepSize = form.cleaned_data['stepSize']
            stepUnit = Enum.TimePeriod(form.cleaned_data['stepUnit'])
            #TODO: tofix
            calendar = Calendar.createCalendar(form.cleaned_data['calendar'])
            confLevel = form.cleaned_data['confLevel']
            pricingDate = Date()
            pricingDate.fromPythonDate(form.cleaned_data['pricingDate'])
            marketId = form.cleaned_data['marketId']
            Settings.instance().evaluationDate = pricingDate.ql()
            P =Portfolio()
            #Generates position on the fly
            modelPositions = portfolio.modelposition_set.filter(asOf=pricingDate)
            if len(modelPositions) == 0:
                return HttpResponse('No positions in portfolio')
            for modelPosition in modelPositions:
                Pos = CreatePosition(modelPosition)
                P.addPosition(Pos) 
            timePeriods = VARUtilities.VARTimePeriodsAndSteps()
            timePeriods.generate(startDate, endDate, stepSize, stepUnit, calendar)

            hvar = HistoricalVAR(pricingDate, P, timePeriods, confLevel, marketId)
            result = hvar.run()
            
            request.session['hVARCache_pnlList'] = hvar.getPnLList()
            request.session['hVARCache_dateList'] = [date.toPythonDate() for date in hvar.getDateList()]
            request.session['hVARCache_pricingDate'] = str(pricingDate)
            request.session['hVARCache_marketId'] = marketId
            request.session['hVARCache_stepSize'] = stepSize
            request.session['hVARCache_stepUnit'] = str(stepUnit)
            request.session['hVARCache_calendar'] = str(calendar)   
            request.session['hVARCache_portfolio'] = portfolio
            request.session['hVARCache_hVARResult'] = round(result * 100, 2)
            request.session['hVARCache_startDate'] = str(startDate)
            request.session['hVARCache_endDate'] = str(endDate)
            request.session['hVARCache_confidenceInterval'] = round(confLevel * 100, 2)
            request.session['hVARCache_mean'] = round(hvar.getMean()*100, 2)
            request.session['hVARCache_standardDeviation'] = round(hvar.getStdDev()*100, 2)
            
            return HttpResponseRedirect('/cmt/hvarPortfolioWithParametersDisplayResults')
        else:
            #if form is not valid then just go back to the url and display errors
            form = HVaRParameters(data=request.POST,\
                                  initial={'pricingDate':request.user.get_profile().location.pricingDate},\
                                  user=request.user)
    else:
        form = HVaRParameters(initial={'endDate':request.user.get_profile().location.pricingDate,
                                       'stepSize':1, 'confLevel':0.95, 
                                       'pricingDate':request.user.get_profile().location.pricingDate,
                                       'marketId':request.user.get_profile().marketId},
                              user=request.user)
 
    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html',
                              {'form': form, 'title':"Historical VaR Report"})

@login_required
@csrf_exempt
@logShort
def hvarPortfolioWithParametersDisplayResults(request):
    return direct_to_template(request,'HistoricalVAR/hVaRReport.html',
                                      {'pricingDate':request.session['hVARCache_pricingDate'],
                                       'marketId':request.session['hVARCache_marketId'],
                                       'stepSize':request.session['hVARCache_stepSize'],
                                       'stepUnit':request.session['hVARCache_stepUnit'],
                                       'calendar':request.session['hVARCache_calendar'],
                                       'portfolio':request.session['hVARCache_portfolio'],
                                       'hVARResult':request.session['hVARCache_hVARResult'],
                                       'startDate':request.session['hVARCache_startDate'],
                                       'endDate':request.session['hVARCache_endDate'],
                                       'confidenceInterval':request.session['hVARCache_confidenceInterval'],
                                       'mean':request.session['hVARCache_mean'],
                                       'standardDeviation':request.session['hVARCache_standardDeviation'],
                                       'title':'Historical VaR'})

@login_required
@csrf_exempt
@logShort
def hvarPortfolioWithParametersCalculatePreConfigured(request):
    if request.method == 'POST':
        form = HVaRParametersPreConfigured(data=request.POST, user=request.user)
        if form.is_valid():
            #if form is valid all fields are fully set and only form submitted
            portfolio = form.cleaned_data['portfolio']
            pricingDate = Date()
            pricingDate.fromPythonDate(form.cleaned_data['pricingDate'])
            configName = form.cleaned_data['config']
            config = HvarConfiguration.objects.get(name=configName)
            startDate = Date()
            startDate.fromPythonDate(config.startDate)
            endDate = Date()
            endDate.fromPythonDate(config.endDate)
            stepSize = config.stepSize
            stepUnit = config.stepUnit
            #TODO: tofix (same as other)
            calendar = config.calendar
            confLevel = config.confLevel
            Settings.instance().evaluationDate = pricingDate.ql()
            P =Portfolio()
            #Generates position on the fly
            modelPositions = portfolio.modelposition_set.filter(asOf=pricingDate)
            if len(modelPositions) == 0:
                return HttpResponse('No positions in portfolio')
            for modelPosition in modelPositions:
                Pos = CreatePosition(modelPosition)
                P.addPosition(Pos) 

            timePeriods = VARUtilities.VARTimePeriodsAndSteps()
            timePeriods.generate(startDate, endDate, stepSize, stepUnit, calendar)
            #TODO Fix decimal to float conversion
            hvar = HistoricalVAR(pricingDate=pricingDate, portfolio=P, 
                                   timeSteps=timePeriods, 
                                   confidenceInterval = float(confLevel), 
                                   marketId = config.marketId)
            result = hvar.run()
            
            request.session['hVARCache_pnlList'] = hvar.getPnLList()
            request.session['hVARCache_dateList'] = [date.toPythonDate() for date in hvar.getDateList()]          
            request.session['hVARCache_pricingDate'] = str(pricingDate)
            request.session['hVARCache_marketId'] = config.marketId
            request.session['hVARCache_stepSize'] = stepSize
            request.session['hVARCache_stepUnit'] = str(stepUnit)
            request.session['hVARCache_calendar'] = str(calendar)   
            request.session['hVARCache_portfolio'] = portfolio
            request.session['hVARCache_hVARResult'] = round(result * 100, 2)
            request.session['hVARCache_startDate'] = str(startDate)
            request.session['hVARCache_endDate'] = str(endDate)
            request.session['hVARCache_confidenceInterval'] = round(confLevel * 100, 2)
            request.session['hVARCache_mean'] = round(hvar.getMean()*100, 2)
            request.session['hVARCache_standardDeviation'] = round(hvar.getStdDev()*100, 2)
            
            return HttpResponseRedirect('/cmt/hvarPortfolioWithParametersDisplayResults')
            
        else:
            #if form is not valid then just go back to the url and display errors
            form = HVaRParametersPreConfigured(data=request.POST,\
                                               initial={'pricingDate':request.user.get_profile().location.pricingDate},\
                                               user=request.user)
    else:
        form = HVaRParametersPreConfigured(initial={'pricingDate':request.user.get_profile().location.pricingDate},\
                                           user=request.user)
 
    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html',
                              {'form': form, 'title':"Historical VaR Report"})

@login_required
@csrf_exempt
def valuationReport(request):
    if request.method == 'POST':
        form = ValuationReportParameters(data=request.POST, user=request.user)
        if form.is_valid():
            portfolio = form.cleaned_data['portfolio']
            marketId = form.cleaned_data['marketId']
            pricingDate = Date()
            pricingDate.fromPythonDate(form.cleaned_data['pricingDate'])
            Settings.instance().evaluationDate = pricingDate.ql()
            P = Portfolio()
            #Generates position on the fly
            modelPositions = portfolio.modelposition_set.filter(asOf=pricingDate)
            if len(modelPositions) == 0:
                return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html',
                                          {'form': form, 'title':"Valuation Report - No Positions",
                                           'message': 'No positions in portfolio'})
            for modelPosition in modelPositions:
                Pos = CreatePosition(modelPosition)
                P.addPosition(Pos) 
            marketDataContainer = MarketDataContainer.MarketDataContainer()
            for p in P.positions:
                marketData = p.marketData(pricingDate, marketId)
                marketDataContainer.add(marketData)
            for p in P.positions:
                p.marketDataContainer = marketDataContainer

            return direct_to_template(request,'HistoricalVAR/valuationReport.html',
                                      {'pricingDate':pricingDate, 'portfolio': portfolio,
                                       'mtm': "%01.2f" % P.NPV(pricingDate, marketId),
                                       'title':'Portfolio Valuation'})
        else:
            form = ValuationReportParameters(data=request.POST, user=request.user)
    else:
        form = ValuationReportParameters(user=request.user,
                                         initial={'marketId':request.user.get_profile().marketId, 
                                                  'pricingDate':request.user.get_profile().location.pricingDate})
 
    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html',
                              {'form': form, 'title':"Valuation Report"})
        
#next 2 functions used for creating graphs and caching data
@logShort
def getxy(request):
    pnlList = request.session['hVARCache_pnlList']
    dateList = request.session['hVARCache_dateList']
    print len(dateList)
    print len(pnlList)
    return dateList[1:], pnlList

@logShort
def createResponse(fig):
    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    plt.clf()
    return response

@login_required
@logShort
def hvarPortfolioWithParameters_graphHistogram(request):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    xdata, ydata = getxy(request)
    ax.hist(ydata, 100)
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('$%1.0f'))
    return createResponse(fig)

@login_required
@logShort
def hvarPortfolioWithParameters_graphLine(request):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    xdata, ydata = getxy(request)
    ax.plot(xdata, ydata)
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('$%1.0f'))
    ax.xaxis.set_major_locator(YearLocator())
    ax.xaxis.set_minor_locator(MonthLocator())
    return createResponse(fig)

import numpy
@login_required
@logShort
def hvarPortfolioWithParameters_graphScatter(request):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    xdata, ydata = getxy(request)
    hist, bins = numpy.histogram(ydata, bins=10)
    ax.plot(bins[0:len(hist)], hist, 'o')
    return createResponse(fig)

@login_required
@logShort
def hvarPortfolioWithParameters_graphPie(request):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    xdata, ydata = getxy(request)
    hist, bins = numpy.histogram(ydata, bins=100)
    ax.pie(hist)
    return createResponse(fig)
    
@login_required
def javaScriptTest(request):
    positions = ModelPosition.objects.all()
    a = "newText1"
    return direct_to_template(request,'HistoricalVAR/javaScriptTest.html',
                              {'positions':positions, 'newText':a})

@login_required
@csrf_exempt
def positionReport(request):
    if request.method == 'POST':
        form = PositionReportParameters(data=request.POST, user=request.user)
        if form.is_valid():
            #the portfolio is actually the portfolio object that is returned
            #and not a string
            portfolio = form.cleaned_data['portfolio']
            pricingDate = Date()
            pricingDate.fromPythonDate(form.cleaned_data['pricingDate'])
            positions = ModelPosition.objects.order_by('portfolio', 'positionType', 'ticker').\
                filter(portfolio=portfolio.id).filter(asOf=pricingDate)
            ret = [(str(p.asOf),portfolio.name, str(p.positionType), str(p.ticker), float(p.amount)) for p in positions ]
            return direct_to_template(request,'HistoricalVAR/positionReport.html',
                              {'jsonPositionData':json.dumps(ret),
                               'title':'Positions in Portfolio'})
        else:
            form = PositionReportParameters(data=request.POST, \
                                            initial={'pricingDate':request.user.get_profile().location.pricingDate},\
                                            user=request.user)
    else:
        form = PositionReportParameters(initial={'pricingDate':request.user.get_profile().location.pricingDate},\
                                        user=request.user)

    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html',
                              {'form': form, 'title':"ModelPosition Report"})
    
@login_required
def simpleSlickGrid(request):
    return direct_to_template(request,'HistoricalVAR/simpleSlickGrid.html')

@login_required
@csrf_exempt
def loadEquityPrices(request):
    if request.method == 'POST':
        form = LoadEquityPrices(request.POST)
        if form.is_valid():
            #if form is valid all fields are fully set and only form submitted
            equity = form.cleaned_data['equity']
            startDate = Date()
            startDate.fromPythonDate(form.cleaned_data['startDate'])
            endDate = Date()
            endDate.fromPythonDate(form.cleaned_data['endDate'])
            marketId = form.cleaned_data['marketId']
            loader = EquityPriceLoader()
            loader.loadHistoricalPricesFromYahoo(secId=equity.ticker, fr=startDate, to=endDate, 
                                                 marketId=marketId)
            return direct_to_template(request,'HistoricalVAR/loadEquityPricesDone.html',
                                        {'ticker':equity.ticker,
                                         'startDate': startDate,
                                         'endDate':endDate})
        else:
            #if form is not valid then just go back to the url and display errors
            form = LoadEquityPrices(request.POST)
    else:
        form = LoadEquityPrices(initial={'endDate':request.user.get_profile().location.pricingDate,
                                         'marketId':request.user.get_profile().marketId})

    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html', 
                              {'form':form, 'title':'Load Equity Prices' }) 

@login_required
@csrf_exempt
def portfolioReport(request):
    portfolios = Portfolio.objects.filter(user=request.user).order_by('name')
    ret = [p.name for p in portfolios ]
    return direct_to_template(request,'HistoricalVAR/portfolioReport.html',
                              {'jsonPortfolioData':json.dumps(ret),
                               'title':'All Portfolios'})

@login_required
def tCBondReport(request):
    bonds = TCBond.objects.all()
    ret = [(b.name, str(b.ccy), str(b.startDate), str(b.endDate), str(b.coupon*100)) for b in bonds]
    return direct_to_template(request,'HistoricalVAR/tCBondsReport.html',
                              {'jsonPortfolioData':json.dumps(ret),
                               'title':'All Bond Definitions'})

@login_required
def tCSwapReport(request):
    swaps = TCSwap.objects.all()
    ret = [(b.name, str(b.ccy), str(b.startDate), str(b.endDate), str(b.fixedCoupon*100), str(b.floatingSpread*10000)) for b in swaps]
    return direct_to_template(request,'HistoricalVAR/tCSwapsReport.html',
                              {'jsonPortfolioData':json.dumps(ret)})
    
@login_required
def identifierReport(request):
    identifiers = Identifier.objects.all()
    ret = [(str(i.type), i.name) for i in identifiers]
    print ret
    return direct_to_template(request,'HistoricalVAR/identifierReport.html',
                              {'jsonIdentifierData':json.dumps(ret)})

    
@login_required
def equityReport(request):
    equities = Equity.objects.all().order_by('ticker')
    ret = [(e.ticker) for e in equities]
    return direct_to_template(request,'HistoricalVAR/equityReport.html',
                              {'jsonEquityData':json.dumps(ret)})
        
@login_required
@csrf_exempt
def portfolio(request):
    '''
    Naming convention of the function is to just list the model
    The view deals with New, Amend and Deleta functions
    '''
    if request.method == 'POST':
        form = PortfolioForm(data=request.POST, user=request.user)
        if form.is_valid():
            _user = form.cleaned_data['user']
            _name = form.cleaned_data['name']
            #if form is valid all fields are fully set and only form submitted
            if 'Save' in request.POST:
                p =Portfolio()
                p.user = _user
                p.name = _name
                p.save()
            elif 'Delete' in request.POST:
                p =Portfolio.objects.filter(user=_user).filter(name=_name)
                if p is not None:
                    p.delete()
            return direct_to_template(request,'HistoricalVAR/displayStaticDataFormDone.html',
                                        {'notification':'Done. Click browser Back to do similar task.'})
        else:
            #if form is not valid then just go back to the url and display errors
            form = PortfolioForm(data=request.POST, user=request.user)
    else:
        form = PortfolioForm(user=request.user)
 
    return direct_to_template(request,'HistoricalVAR/displayStaticDataForm.html', 
                              {'form': form, 'title':"Portfolio Maintenance"})

@login_required
@csrf_exempt
def tCBond(request):
    '''
    Naming convention of the function is to just list the model
    The view deals with New, Amend and Deleta functions
    '''
    if request.method == 'POST':
        form = TCBondForm(data=request.POST)
        if form.is_valid():
            if 'Save' in request.POST:
                form.save()
            elif 'Delete' in request.POST:
                a = TCBond.objects.filter(name=form.cleaned_data['name'])
                if a is not None:
                    a.delete()
            return direct_to_template(request,'HistoricalVAR/displayStaticDataFormDone.html',
                                      {'notification':'Done. Click browser Back to do similar task.'})
        else:
            #if form is not valid then just go back to the url and display errors
            form = TCBondForm(data=request.POST)
    else:
        form = TCBondForm()
 
    return direct_to_template(request,'HistoricalVAR/displayStaticDataForm.html', 
                              {'form': form, 'title':"Bond Terms&Conditions Maintenance"})

@login_required
@csrf_exempt
def tCSwap(request):
    '''
    Naming convention of the function is to just list the model
    The view deals with New, Amend and Deleta functions
    '''
    if request.method == 'POST':
        form = TCSwapForm(data=request.POST)
        if form.is_valid():
            if 'Save' in request.POST:
                form.save()
            elif 'Delete' in request.POST:
                a = TCSwap.objects.filter(name=form.cleaned_data['name'])
                if a is not None:
                    a.delete()
            return direct_to_template(request,'HistoricalVAR/displayStaticDataFormDone.html',
                                      {'notification':'Done. Click browser Back to do similar task.'})
        else:
            #if form is not valid then just go back to the url and display errors
            form = TCSwapForm(data=request.POST)
    else:
        form = TCSwapForm()
 
    return direct_to_template(request,'HistoricalVAR/displayStaticDataForm.html', 
                              {'form': form, 'title':"Swap Terms&Conditions Maintenance"})

@login_required
@csrf_exempt
def identifier(request):
    '''
    Naming convention of the function is to just list the model
    The view deals with New, Amend and Deleta functions
    '''
    if request.method == 'POST':
        form = IdentifierForm(data=request.POST)
        if form.is_valid():
            if 'Save' in request.POST:
                form.save()
            elif 'Delete' in request.POST:
                a = Identifier.objects.filter(name=form.cleaned_data['name']).filter(type=form.cleaned_data['type'])
                if a is not None:
                    a.delete()
            return direct_to_template(request,'HistoricalVAR/displayStaticDataFormDone.html',
                                      {'notification':'Done. Click browser Back to do similar task.'})
        else:
            #if form is not valid then just go back to the url and display errors
            form = IdentifierForm(data=request.POST)
    else:
        form = IdentifierForm()
 
    return direct_to_template(request,'HistoricalVAR/displayStaticDataForm.html', 
                              {'form': form, 'title':"Bond Identifier Maintenance"})

@login_required
@csrf_exempt
def equity(request):
    '''
    Naming convention of the function is to just list the model
    The view deals with New, Amend and Deleta functions
    '''
    if request.method == 'POST':
        form = EquityForm(data=request.POST)
        if form.is_valid():
            if 'Save' in request.POST:
                form.save()
            elif 'Delete' in request.POST:
                a = Equity.objects.filter(ticker=form.cleaned_data['ticker'])
                if a is not None:
                    a.delete()
            return direct_to_template(request,'HistoricalVAR/displayStaticDataFormDone.html',
                                      {'notification':'Done. Click browser Back to do similar task.'})
        else:
            #if form is not valid then just go back to the url and display errors
            form = EquityForm(data=request.POST)
    else:
        form = EquityForm()
 
    return direct_to_template(request,'HistoricalVAR/displayStaticDataForm.html', 
                              {'form': form, 'title':"Equity Maintenance"})

@login_required
@csrf_exempt
def position(request):
    '''
    Naming convention of the function is to just list the model
    The view deals with New, Amend and Delete functions
    '''
    if request.method == 'POST':
        form = PositionForm(user=request.user, data=request.POST)
        if form.is_valid():
            if 'Save' in request.POST:
                form.save()
            elif 'Delete' in request.POST:
                raise ErrorHandling.OtherException('Not yet implemented')
                a = ModelPosition.objects.filter(ticker=form.cleaned_data['ticker'])
                if a is not None:
                    a.delete()
            return direct_to_template(request,'HistoricalVAR/displayStaticDataFormDone.html',
                                      {'notification':'Done. Click browser Back to do similar task.'})
        else:
            #if form is not valid then just go back to the url and display errors
            form = PositionForm(user=request.user,data=request.POST)
    else:
        form = PositionForm(user=request.user)
 
    return direct_to_template(request,'HistoricalVAR/displayStaticDataForm.html', 
                              {'form': form, 'title':"ModelPosition Maintenance"})

@login_required
@csrf_exempt
def interestRateCurveReportCalculate(request):
    if request.method == 'POST':
        form = InterestRateCurveReportParameters(request.POST)
        if form.is_valid():
            ccy = form.cleaned_data['ccy']
            index = form.cleaned_data['index']
            term = form.cleaned_data['term']
            numTerms = form.cleaned_data['numTerms']
            pricingDate = Date()
            pricingDate.fromPythonDate(form.cleaned_data['pricingDate'])
            marketId = form.cleaned_data['marketId']
            curve = InterestRateCurve(ccy=ccy, index=index, term=term, 
                                  numTerms=numTerms, pricingDate=pricingDate, marketId=marketId)
            curve.load()
            curveToDisplay = [(r.type, str(r.numTerms)+str(r.term), str(r.mid*100.0)) for r in curve.rates]

            Settings.instance().evaluationDate = pricingDate.ql()
            zeroCurve = curve.buildZeroCurve()
            
            zeroCurveToDisplay = [(createPythonDateFromQLDate(qlDate=node[0]), str(node[1])) for node in zeroCurve.nodes()]

            request.session['rateCurve_curve'] = curveToDisplay
            request.session['rateCurve_zeroCurve'] = zeroCurveToDisplay
            request.session['rateCurve_ccy'] = ccy
            request.session['rateCurve_index'] = index
            request.session['rateCurve_term'] = term 
            request.session['rateCurve_numTerms'] = numTerms
            request.session['rateCurve_pricingDate'] = str(pricingDate) 
            request.session['rateCurve_marketId'] = marketId

            return HttpResponseRedirect('/cmt/interestRateCurveReportDisplay')            
        else:
            form = InterestRateCurveReportParameters(request.POST)
    else:
        form = InterestRateCurveReportParameters(initial={'ccy': Enum.Currency('USD'),
                                                          'index':Enum.Index('LIBOR'),
                                                          'term':Enum.TimePeriod('M'),
                                                          'numTerms':3,
                                                          'pricingDate':request.user.get_profile().location.pricingDate,
                                                          'marketId':request.user.get_profile().marketId})
 
    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html', 
                              {'form':form, 'title':'Interest Rate Curve' }) 
    

@login_required
@csrf_exempt
def interestRateCurveReportDisplay(request):
    title = str(request.session['rateCurve_ccy'])+'\\'+str(request.session['rateCurve_index'])+'\\'
    title += str(request.session['rateCurve_term'])
    title += str(request.session['rateCurve_numTerms'])
    title += ' as of ' + str(request.session['rateCurve_pricingDate'])
    title += ' and market id ' + str(request.session['rateCurve_marketId'])
    
 #   <label>{{ccy}}/{{index}}/{{numTerms}}{{term}}/{{marketId}} with pricing date {{pricingDate}}</label>
    return direct_to_template(request,'HistoricalVAR/interestRateCurveReport.html',
                              {'title': title,
                               'ccy': request.session['rateCurve_ccy'],
                               'index': request.session['rateCurve_index'],
                               'term': request.session['rateCurve_term'],
                               'numTerms': request.session['rateCurve_numTerms'],
                               'pricingDate': request.session['rateCurve_pricingDate'],
                               'marketId': request.session['rateCurve_marketId'],
                               'jsonIdentifierData':\
                               json.dumps(request.session['rateCurve_curve'])})

def interestRateCurveReportGraph(request):
    zeroCurve = request.session['rateCurve_zeroCurve']
    fig = plt.figure()
    ax = fig.add_subplot(111)
    #dates should be converted into python dates for graph display
    dates = [item[0] for item in zeroCurve]
    rates = [float(item[1])*100 for item in zeroCurve]
    ax.plot(dates, rates)
#   ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%1.0f'))
    ax.xaxis.set_major_locator(YearLocator())
    fig.autofmt_xdate()
#    import matplotlib.dates as mdates
 #   ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
    #ax.xaxis.date()
#    ax.xaxis.set_minor_locator(MonthLocator())
    #print dates
    #print rates
    return createResponse(fig)    

    #xdata, ydata = getxy(request)
    #ax.plot(xdata, ydata)
    #ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('$%1.0f'))
    #ax.xaxis.set_major_locator(YearLocator())
    #ax.xaxis.set_minor_locator(MonthLocator())
    #return createResponse(fig)


@login_required
@csrf_exempt
def portfolioBenchmarkCorrelationReport(request):
    if request.method == 'POST':
        form = CorrelationReportParameters(data=request.POST, user=request.user)
        if form.is_valid():
            portfolio = form.cleaned_data['portfolio']
            benchmark = form.cleaned_data['benchmark']
            startDate = Date()
            startDate.fromPythonDate(form.cleaned_data['startDate'])
            endDate = Date()
            endDate.fromPythonDate(form.cleaned_data['endDate'])
            stepSize = form.cleaned_data['stepSize']
            stepUnit = Enum.TimePeriod(form.cleaned_data['stepUnit'])
            calendar = Calendar.createCalendar(form.cleaned_data['calendar'])
            pricingDate = Date()
            pricingDate.fromPythonDate(form.cleaned_data['pricingDate'])
            marketId = form.cleaned_data['marketId']
            Settings.instance().evaluationDate = pricingDate.ql()
            
            #Create P&L vector for portfolio
            timePeriods = VARUtilities.VARTimePeriodsAndSteps()
            timePeriods.generate(startDate, endDate, stepSize, stepUnit, calendar)

            P1 =Portfolio()
            modelPositions = portfolio.modelposition_set.filter(asOf=pricingDate)
            if len(modelPositions) == 0:
                return HttpResponse('No positions in portfolio')
            for modelPosition in modelPositions:
                Pos = CreatePosition(modelPosition)
                P1.addPosition(Pos) 
            hvar1 = HistoricalVAR(pricingDate, P1, timePeriods, 0.99, marketId)
            hvar1.run()
            
            P2 =Portfolio()
            modelPosition = ModelPosition(portfolio=P2,
                                          positionType=Enum.PositionType('EQUITY'),
                                          ticker=benchmark.ticker,
                                          amount=100,
                                          asOf=pricingDate)
            P2.addPosition(CreatePosition(modelPosition))
            hvar2 = HistoricalVAR(pricingDate, P2, timePeriods, 0.99, marketId)
            hvar2.run()

            pearsonCorr = pearsonr(hvar1.getPnLList(), hvar2.getPnLList())
            
            return direct_to_template(request,'HistoricalVAR/correlationReport.html',
                                      {'pricingDate':pricingDate,
                                       'marketId':marketId,
                                       'stepSize':stepSize,
                                       'stepUnit':stepUnit,
                                       'calendar':calendar,
                                       'portfolio': portfolio,
                                       'benchmark': benchmark,
                                       'startDate': startDate,
                                       'endDate':endDate,
                                       'mean1':'Not calculated',
                                       'mean2':'Not calculated',
                                       'standardDeviation1':'Not calculated',
                                       'standardDeviation2':'Not calculated',
                                       'correlation':pearsonCorr[0],
                                       'covariance':'Not calculated'})
        else:
            #if form is not valid then just go back to the url and display errors
            form = CorrelationReportParameters(data=request.POST,\
                                  initial={'pricingDate':request.user.get_profile().location.pricingDate},\
                                  user=request.user)
    else:
        form = CorrelationReportParameters(initial={'endDate':request.user.get_profile().location.pricingDate,
                                                    'stepSize':1, 
                                                    'pricingDate':request.user.get_profile().location.pricingDate,
                                                    'marketId':request.user.get_profile().marketId},
                                           user=request.user)
 
    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html',
                              {'form': form, 'title':"Correlation Report"})
        
@login_required
@csrf_exempt
def bondCalculator(request):
    if request.method == 'POST':
        form = TCBondCalculatorForm(data=request.POST, 
                          initial={'pricingDate':request.user.get_profile().location.pricingDate,
                                   'marketId':request.user.get_profile().marketId})
        if form.is_valid():
            #strange syntax but it seems the way to do it
            pricingDate = Date()
            pricingDate.fromPythonDate(form.cleaned_data['pricingDate'])
            marketId = form.cleaned_data['marketId']
            tcBond = form.save(commit=False)
            bondPosition = BondPosition(amount=1.0, secId=tcBond.name, tcBond=tcBond)
            marketDataContainer = MarketDataContainer.MarketDataContainer()
            marketData = bondPosition.marketData(pricingDate=pricingDate, 
                                                 marketId=marketId)
            marketDataContainer.add(marketData)
            bondPosition.marketDataContainer = marketDataContainer
            return direct_to_template(request,'HistoricalVAR/displayCalculatorForm.html',
                                      {'form': form, 
                                       'price': '$ '+str(round(bondPosition.NPV(pricingDate=pricingDate, 
                                                                 marketId=marketId),2)),
                                       'title':"Bond Calculator Results for $100 Notional"})
        else:
            #if form is not valid then just go back to the url and display errors
            form = TCBondCalculatorForm(data=request.POST, 
                              initial={'pricingDate':request.user.get_profile().location.pricingDate,
                                       'marketId':request.user.get_profile().marketId})
    else:
        form = TCBondCalculatorForm(initial={'pricingDate':request.user.get_profile().location.pricingDate,
                                   'marketId':request.user.get_profile().marketId,
                                   'name':'Not Needed'})
 
    return direct_to_template(request,'HistoricalVAR/displayCalculatorForm.html', 
                              {'form': form, 'title':"Bond Calculator Input for $100 Notional"})

@login_required
@csrf_exempt
def swapCalculator(request):
    print 'In swapCalculator ' + str(request.user.get_profile().location.pricingDate)
    if request.method == 'POST':
        form = TCSwapCalculatorForm(data=request.POST, 
                          initial={'pricingDate':request.user.get_profile().location.pricingDate,
                                   'marketId':request.user.get_profile().marketId})
        if form.is_valid():
            #strange syntax but it seems the way to do it
            print 'Form is valid'
            pricingDate = Date()
            pricingDate.fromPythonDate(form.cleaned_data['pricingDate'])
            marketId = form.cleaned_data['marketId']
            tcSwap = form.save(commit=False)
            swapPosition = SwapPosition(amount=1000000, secId='dummy', tcSwap=tcSwap)
            marketDataContainer = MarketDataContainer.MarketDataContainer()
            marketData = swapPosition.marketData(pricingDate=pricingDate, 
                                                 marketId=marketId)
            marketDataContainer.add(marketData)
            swapPosition.marketDataContainer = marketDataContainer
            #TODO: Fix this call. It should not be necessary to call
            swapPosition._setupQL(pricingDate=pricingDate, marketId=marketId)
            return direct_to_template(request,'HistoricalVAR/displayCalculatorForm.html',
                                      {'form': form, 
                                       'price': '$ '+str(round(swapPosition.NPV(pricingDate=pricingDate, 
                                                                 marketId=marketId),2)),
                                       'fairRate': str(round(swapPosition.fairRate(pricingDate=pricingDate, 
                                                                 marketId=marketId)*100,2))+' %',
                                       'fairSpread': str(round(swapPosition.fairSpread(pricingDate=pricingDate, 
                                                                 marketId=marketId)*10000,2))+' bp',
                                       'floatingLegBPS': '$ ' + str(round(swapPosition.floatingLegBPS(pricingDate=pricingDate, 
                                                                 marketId=marketId),2)),
                                       'fixedLegBPS': '$ ' + str(round(swapPosition.fixedLegBPS(pricingDate=pricingDate, 
                                                                 marketId=marketId),2)),
                                       'title':"Swap Calculator Results for $1M Notional"})
        else:
            #if form is not valid then just go back to the url and display errors
            print 'Form is not valid'
            form = TCSwapCalculatorForm(data=request.POST, 
                              initial={'pricingDate':request.user.get_profile().location.pricingDate,
                                       'marketId':request.user.get_profile().marketId})
    else:
        print 'unexpected'
        form = TCSwapCalculatorForm(initial={'pricingDate':request.user.get_profile().location.pricingDate,
                                   'marketId':request.user.get_profile().marketId,
                                   'name':'Not Needed'})
 
    return direct_to_template(request,'HistoricalVAR/displayCalculatorForm.html', 
                              {'form': form, 'title':"Swap Calculator for $1M Notional"})

@login_required
@csrf_exempt
def location(request):
    '''
    Naming convention of the function is to just list the model
    '''
    if request.method == 'POST':
        form = LocationForm(data=request.POST)
        if form.is_valid():
            if 'Save' in request.POST:
                location = Location.objects.get(name=request.user.get_profile().location.name)
                location.pricingDate = form.cleaned_data['pricingDate']
                location.save()
            elif 'Delete' in request.POST:
                raise ErrorHandling.OtherException('Delete not valid')
            return direct_to_template(request,'HistoricalVAR/displayStaticDataFormDone.html',
                                      {'notification':'Done. Click browser Back to do similar task.'})
        else:
            #if form is not valid then just go back to the url and display errors
            form = LocationForm(data=request.POST)
    else:
        form = LocationForm(initial={'name':request.user.get_profile().location.name,
                                     'pricingDate':request.user.get_profile().location.pricingDate})
 
    return direct_to_template(request,'HistoricalVAR/displayStaticDataForm.html', 
                              {'form': form, 'title':"Location Maintenance"})

@login_required
@csrf_exempt
def userProfile(request):
    '''
    Naming convention of the function is to just list the model
    '''
    if request.method == 'POST':
        form = UserProfileForm(data=request.POST)
        if form.is_valid():
            if 'Save' in request.POST:
                user = User.objects.get(username=request.user.username)
                userProfile = UserProfile.objects.get(user=user)
                userProfile.location = form.cleaned_data['location']
                userProfile.marketId = form.cleaned_data['marketId']
                userProfile.save()
            elif 'Delete' in request.POST:
                raise ErrorHandling.OtherException('Delete not valid')
            return direct_to_template(request,'HistoricalVAR/displayStaticDataFormDone.html',
                                      {'notification':'Done. Click browser Back to do similar task.'})
        else:
            #if form is not valid then just go back to the url and display errors
            form = UserProfileForm(data=request.POST)
    else:
        user = User.objects.get(username=request.user.username)
        form = UserProfileForm(initial={'user':user,
                                        'location':request.user.get_profile().location,
                                        'marketId':request.user.get_profile().marketId})
 
    return direct_to_template(request,'HistoricalVAR/displayStaticDataForm.html', 
                              {'form': form, 'title':"User Profile Maintenance"})
    
@login_required
@csrf_exempt
def loadMissingMarketDataForPortfolio(request):
    if request.method == 'POST':
        form = LoadMissingMarketDataForPortfolioForm(data=request.POST)
        if form.is_valid():
            portfolio = form.cleaned_data['portfolio']
            startDate = Date()
            startDate.fromPythonDate(form.cleaned_data['startDate'])
            endDate = Date()
            endDate.fromPythonDate(form.cleaned_data['endDate'])
            calendar = Calendar.createCalendar(form.cleaned_data['calendar'])
            marketId = form.cleaned_data['marketId']
            raise ErrorHandling.OtherException('modelposition_set needs to be fixed because multiple dates needed. Different dates can have different positions.')
            modelPositions = portfolio.modelposition_set.filter(asOf=pricingDate)
            if len(modelPositions) == 0:
                return HttpResponse('No positions in portfolio')
            timePeriods = VARUtilities.VARTimePeriodsAndSteps()
            timePeriods.generate(start=startDate, end=endDate, num=1, 
                                 term=Enum.TimePeriod('D'), calendar=calendar)
            updated = False #indicates if we did any saving
            for timeStep in timePeriods.timeSteps:
                Settings.instance().evaluationDate = timeStep.ql()
                for modelPosition in modelPositions:
                    pos = CreatePosition(modelPosition)
                    try:
                        pos.marketData(timeStep, marketId)
                    except ErrorHandling.MarketDataMissing:
                        pos.loadAndSaveMarketData(timeStep, marketId)
                        updated = True
            if updated == True:
                notification = 'Market data was added'
            else:
                notification = 'All market data was already up to date'
            return direct_to_template(request,'HistoricalVAR/displayStaticDataFormDone.html',
                                      {'notification':notification})
        else:
            #if form is not valid then just go back to the url and display errors
            form = LoadMissingMarketDataForPortfolioForm(data=request.POST)
    else:
        form = LoadMissingMarketDataForPortfolioForm(initial={'marketId':request.user.get_profile().marketId,
                                                              'startDate':request.user.get_profile().location.pricingDate,
                                                              'endDate':request.user.get_profile().location.pricingDate})
 
    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html', 
                              {'form': form, 'title':"Load Missing Market Data for Portfolio"})

@login_required
@csrf_exempt
def allPortfolioDetailsReport(request):
    ret = []
    pricingDate = Date()
    pricingDate.fromPythonDate(request.user.get_profile().location.pricingDate)
    Settings.instance().evaluationDate = pricingDate.ql()
    marketId = request.user.get_profile().marketId
    portfolios =Portfolio.objects.filter(user=request.user)
    totalValue = 0
    for portfolio in portfolios:
        modelPositions = portfolio.modelposition_set.filter(asOf=pricingDate)
        for modelPosition in modelPositions:
            position = CreatePosition(modelPosition)
            marketDataContainer = MarketDataContainer.MarketDataContainer()
            marketDataContainer.add(position.marketData(pricingDate=pricingDate,marketId=marketId))
            position.marketDataContainer = marketDataContainer
            value = position.NPV(pricingDate=pricingDate, marketId=marketId)
            totalValue += value
            if value <> 0.0:
                ret.append((portfolio.name, str(modelPosition.positionType), modelPosition.ticker, 
                            str(modelPosition.amount), Converter.fToDC(floatValue=value)))
    ret.append(('TOTAL', '','','',Converter.fToDC(floatValue=totalValue)))
    return direct_to_template(request,'HistoricalVAR/allPortfolioDetailsReport.html',
                              {'jsonPositionData':json.dumps(ret),
                               'title':'Details for all portfolios'})
            
@login_required
def transactionReport(request):
    transactions = Transaction.objects.all()
    ret = [(t.portfolio.name,str(t.transactionType),str(t.positionType),t.ticker,\
            str(t.amount),str(t.transactionDate),str(t.effectiveDate)) for t in transactions]
    return direct_to_template(request,'HistoricalVAR/transactionReport.html',
                              {'jsonTransactionData':json.dumps(ret)})
   
@login_required
@csrf_exempt
def transaction(request):
    '''
    Naming convention of the function is to just list the model
    The view deals with New, Amend and Deleta functions
    '''
    if request.method == 'POST':
        form = TransactionForm(user=request.user, data=request.POST)
        if form.is_valid():
            if 'Save' in request.POST:
                form.save()
            elif 'Delete' in request.POST:
                raise ErrorHandling.OtherException('Not yet implemented')
            return direct_to_template(request,'HistoricalVAR/displayStaticDataFormDone.html',
                                      {'notification':'Done. Click browser Back to do similar task.'})
        else:
            #if form is not valid then just go back to the url and display errors
            form = TransactionForm(user=request.user,data=request.POST)
            
    else:
        form = TransactionForm(user=request.user)
 
    return direct_to_template(request,'HistoricalVAR/displayStaticDataForm.html', 
                              {'form': form, 'title':"Transaction Maintenance"})

@login_required
@csrf_exempt
def assetAllocationGraph(request):
    return direct_to_template(request,'HistoricalVAR/assetAllocationGraph.html',
                              {'title':'Asset Allocation'})
            
@login_required
@csrf_exempt
def overview(request):
    return direct_to_template(request,'HistoricalVAR/overview.html',
                              {'title':'Overview'})
            
@login_required
@csrf_exempt
def batch(request):
    if request.method == 'POST':
        form = BatchForm(data=request.POST)
        if form.is_valid():
            batchDate = Date()
            batchDate.fromPythonDate(form.cleaned_data['batchDate'])
            batch = BatchUtility(batchDate=batchDate)
            batch.run()
            batch.sendEmail()
            return direct_to_template(request,'HistoricalVAR/displayStaticDataFormDone.html',
                                      {'notification':'Batch done for '+str(batchDate)+'. Click browser Back to do similar task.'})
        else:
            #if form is not valid then just go back to the url and display errors
            form = BatchForm(data=request.POST,initial={'pricingDate':request.user.get_profile().location.pricingDate})
            
    else:
        form = BatchForm(initial={'pricingDate':request.user.get_profile().location.pricingDate})
 
    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html', 
                              {'form': form, 'title':"Batch Run"})
    
@login_required
@csrf_exempt
def multiBatches(request):
    if request.method == 'POST':
        form = MultiBatchesForm(data=request.POST)
        if form.is_valid():
            startDate = Date()
            startDate.fromPythonDate(form.cleaned_data['startDate'])
            endDate = Date()
            endDate.fromPythonDate(form.cleaned_data['endDate'])
            batchDate = startDate
            while batchDate <= endDate:
                batch = BatchUtility(batchDate=batchDate)
                batch.run()
                batch.sendEmail()
                batchDate.nextDay()
            return direct_to_template(request,'HistoricalVAR/displayStaticDataFormDone.html',
                                      {'notification':'Done. Click browser Back to do similar task.'})
        else:
            #if form is not valid then just go back to the url and display errors
            form = MultiBatchesForm(data=request.POST, initial={'startDate':request.user.get_profile().location.pricingDate,
                                                                'endDate':request.user.get_profile().location.pricingDate,
                                                                'marketId':request.user.get_profile().marketId})
            
    else:
        form = MultiBatchesForm()
 
    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html', 
                              {'form': form, 'title':"Batch Run Over Time Period"})

@login_required
@csrf_exempt
def performanceReport(request):
    if request.method == 'POST':
        form = PerformanceReportParameters(data=request.POST, user=request.user)
        if form.is_valid():
            ret = []
            startDate = Date()
            startDate.fromPythonDate(form.cleaned_data['startDate'])
            endDate = Date()
            endDate.fromPythonDate(form.cleaned_data['endDate'])
            marketId = form.cleaned_data['marketId']
#            Settings.instance().evaluationDate = pricingDate.ql()
            portfolios = Portfolio.objects.filter(user=request.user)
            totalStart = 0
            totalEnd = 0
            for portfolio in portfolios:
                startValue = 0
                endValue = 0
                performanceCalculator = PerformanceCalculator(start=startDate,
                                                              end=endDate,
                                                              portfolio=portfolio,
                                                              marketId=marketId)
                performanceCalculator.calc()
                startValue = performanceCalculator.startValue
                endValue = performanceCalculator.endValue
                endValue += performanceCalculator.transactionValue
                totalStart += startValue
                totalEnd += endValue
                if startValue == 0:
                    overallPerformance = 0
                else:
                    overallPerformance = ((endValue - startValue) / startValue) * 365.0 / (endDate.ql() - startDate.ql())
            #for now only report overal performance accross all portfolios for that user
            #later amend the performance calculator generically to report on portfolio level
            #TODO: Check if decimals are returned to front-end of percentages
                periodPerformance = overallPerformance*100.0/365.0*(endDate.ql() - startDate.ql())
                annualPerformance = overallPerformance*100.0
                ret.append((portfolio.name, Converter.fToDC(floatValue=startValue), Converter.fToDC(floatValue=endValue),
                            Converter.fToDC(floatValue=periodPerformance),Converter.fToDC(floatValue=annualPerformance)))
            if totalStart == 0:
                overallPerformance = 0
            else:
                overallPerformance = ((totalEnd - totalStart) / totalStart) * 365.0 / (endDate.ql() - startDate.ql())
            #for now only report overal performance accross all portfolios for that user
            #later amend the performance calculator generically to report on portfolio level
            #TODO: Check if decimals are returned to front-end of percentages
                periodPerformance = overallPerformance*100.0/365.0*(endDate.ql() - startDate.ql())
                annualPerformance = overallPerformance*100.0
            
            ret.append(('','','','',''))
            ret.append(('TOTAL', Converter.fToDC(floatValue=totalStart), Converter.fToDC(floatValue=totalEnd),
                        Converter.fToDC(floatValue=periodPerformance),Converter.fToDC(floatValue=annualPerformance)))
                        
            return direct_to_template(request,'HistoricalVAR/performanceReport.html',
                                      {'title':'Performance Report from '+str(startDate)+' to '+str(endDate),
                                       'reportData':json.dumps(ret)})
        else:
            #if form is not valid then just go back to the url and display errors
            form = PerformanceReportParameters(data=request.POST,
                                               initial={'endDate':request.user.get_profile().location.pricingDate,
                                                        'marketId':request.user.get_profile().marketId}, user=request.user)
    else:
        form = PerformanceReportParameters(initial={'endDate':request.user.get_profile().location.pricingDate,
                                                    'marketId':request.user.get_profile().marketId}, user=request.user)
 
    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html',
                              {'form': form, 'title':"Performance Report"})
        
@login_required
def assetAllocationReport(request):
    if request.method == 'POST':
        form = AssetAllocationReportParameters(data=request.POST, user=request.user)
        if form.is_valid():
            ret = []
            pricingDate = Date()
            pricingDate.fromPythonDate(form.cleaned_data['pricingDate'])
            marketId = form.cleaned_data['marketId']
#            Settings.instance().evaluationDate = pricingDate.ql()
            allocations = {}
            totalValue = 0
            for item in Enum.AssetType.choices:
                allocations[item[0]] = 0
            portfolios =Portfolio.objects.filter(user=request.user)
            for portfolio in portfolios:
                if portfolio.name == 'TradeAug2013':
                    continue
                modelPositions = ModelPosition.objects.filter(portfolio=portfolio, asOf=pricingDate)
                for modelPosition in modelPositions:
                    position = CreatePosition(modelPosition)
                    portfolio.addPosition(position)
                marketDataContainer = MarketDataContainer.MarketDataContainer()
                for position in portfolio.positions:
                    marketDataContainer.add(position.marketData(pricingDate=pricingDate, marketId=marketId))
                for position in portfolio.positions:
                    position.marketDataContainer = marketDataContainer
                for position in portfolio.positions:
                    npv = position.NPV(pricingDate=pricingDate, marketId=marketId)
                    print portfolio.name + "\t" + str(position.getAssetType())
                    allocations[str(position.getAssetType())] += npv
                    print allocations
                    totalValue += npv
        
            orderedAllocations = OrderedDict(sorted(allocations.items(),key=lambda t: t[1],reverse=True))
            for key in orderedAllocations.keys():
                try:
                    allocationPercent = Allocation.objects.get(assetType=Enum.AssetType(key)).percent
                except:
                    allocationPercent = 0.0
                try:
                    actualAllocation = 100*orderedAllocations[key]/totalValue
                except:
                    actualAllocation = 0.0
                ret.append((key, Converter.fToDC(floatValue=actualAllocation), Converter.fToDC(floatValue=100*allocationPercent),
                            Converter.fToDC(floatValue=orderedAllocations[key])))

            return direct_to_template(request,'HistoricalVAR/assetAllocationReport.html',
                                      {'title':'Asset Allocation Report',
                                       'reportData':json.dumps(ret)})
        else:
            #if form is not valid then just go back to the url and display errors
            form = AssetAllocationReportParameters(data=request.POST,
                                               initial={'pricingDate':request.user.get_profile().location.pricingDate,
                                                        'marketId':request.user.get_profile().marketId}, user=request.user)
    else:
        form = AssetAllocationReportParameters(initial={'pricingDate':request.user.get_profile().location.pricingDate,
                                                        'marketId':request.user.get_profile().marketId}, user=request.user)
 
    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html',
                              {'form': form, 'title':"Asset Allocation Report"})

@login_required
@csrf_exempt
def netWorthTrendReport(request):
    if request.method == 'POST':
        form = NetWorthTrendReportParameters(data=request.POST, user=request.user)
        if form.is_valid():
            ret = []
            startDate = Date()
            startDate.fromPythonDate(form.cleaned_data['startDate'])
            endDate = Date()
            endDate.fromPythonDate(form.cleaned_data['endDate'])
            marketId = form.cleaned_data['marketId']
            portfolios = Portfolio.objects.filter(user=request.user)
            ret = []
            parameters = TimeSeriesNPVCalculatorParameters(start=startDate, end=endDate,
                                                           marketId=marketId, portfolios=portfolios)
            calculator = TimeSeriesNPVCalculator(parameters=parameters)
            calculator.calc()
            results = calculator.results()
            print calculator.results()
            for result in results:
                ret.append((str(result[0]),Converter.fToDC(result[1])))
            return direct_to_template(request,'HistoricalVAR/netWorthTrendReport.html',
                                        {'title':'Networth Trend from '+str(startDate)+' to '+str(endDate),
                                         'reportData':json.dumps(ret)})
        else:
            #if form is not valid then just go back to the url and display errors
            form = NetWorthTrendReportParameters(data=request.POST,
                                               initial={'endDate':request.user.get_profile().location.pricingDate,
                                                        'marketId':request.user.get_profile().marketId}, user=request.user)
    else:
        form = NetWorthTrendReportParameters(initial={'endDate':request.user.get_profile().location.pricingDate,
                                                    'marketId':request.user.get_profile().marketId}, user=request.user)
 
    return direct_to_template(request,'HistoricalVAR/displayReportParameterForm.html',
                              {'form': form, 'title':"Networth Trend Report"})
        
        
