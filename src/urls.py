from django.conf.urls.defaults import *
from django.contrib import admin
from ajax_select import urls as ajax_select_urls
import settings
admin.autodiscover()

urlpatterns = patterns('cmt.src.views',
    (r'^$', 'home'),
    (r'^altGUI/$', 'altGUI'),
#    (r'^base_test1/$', 'show_base_test1',),
    (r'^googleChartAPITest/$', 'googleChartAPITest',),
    (r'^chartTest/$', 'chartTest',),
    (r'^excelTest/$', 'excelTest',),
    (r'^showEquityPrices/$', 'showEquityPrices',),
    (r'^showEquityPricesExcel/$', 'showEquityPricesExcel',),   
    (r'^loadEquityPrices/$', 'loadEquityPrices',),
    #Display Interest Rate Report and Graph
    (r'^interestRateCurveReportCalculate/$', 'interestRateCurveReportCalculate'),
    (r'^interestRateCurveReportDisplay/$', 'interestRateCurveReportDisplay'),
    (r'^interestRateCurveReportDisplay/graphZeroRateCurve.png$', 'interestRateCurveReportGraph'),
#    (r'^hvarPortfolioWithParametersDisplayResults/graphScatter.png/$', 'hvarPortfolioWithParameters_graphScatter'),
#    graphCurveZeroRates.png
    #Calculates results and then redirects to DisplayResults. This ensures that 
    #we have synchronization between spreadsheet display and graphs
    (r'^hvarPortfolioWithParametersCalculate/$', 'hvarPortfolioWithParametersCalculate',),
    (r'^hvarPortfolioWithParametersDisplayResults/$', 'hvarPortfolioWithParametersDisplayResults',),
    (r'^hvarPortfolioWithParametersDisplayResults/graphHistogram.png/$', 'hvarPortfolioWithParameters_graphHistogram'),
    (r'^hvarPortfolioWithParametersDisplayResults/graphLine.png/$', 'hvarPortfolioWithParameters_graphLine'),
    (r'^hvarPortfolioWithParametersDisplayResults/graphScatter.png/$', 'hvarPortfolioWithParameters_graphScatter'),
    (r'^hvarPortfolioWithParametersDisplayResults/graphPie.png/$', 'hvarPortfolioWithParameters_graphPie'),
    (r'^hvarPortfolioWithParametersCalculatePreConfigured/$', 'hvarPortfolioWithParametersCalculatePreConfigured',),
#    (r'^portfolioPortfolioCorrelation/$', 'portfolioPortfolioCorrelation',),
#    (r'^portfolioPortfolioCorrelationPreConfigured/$', 'portfolioPortfolioCorrelationPreConfigured',),
    (r'^portfolioBenchmarkCorrelation/$', 'portfolioBenchmarkCorrelationReport',),
#    (r'^portfolioBenchmarkCorrelationPreConfigured/$', 'portfolioBenchmarkCorrelationPreConfigured',),
    #The following is for static data    
    (r'^positionReport/$', 'positionReport',),
    (r'^transactionReport/$', 'transactionReport',),
    (r'^portfolioReport/$', 'portfolioReport',),
    (r'^tCBondReport/$', 'tCBondReport',),
    (r'^tCSwapReport/$', 'tCSwapReport',),
    (r'^identifierReport/$', 'identifierReport',),
    (r'^equityReport/$', 'equityReport',),
    (r'^allPortfolioDetailsReport/$', 'allPortfolioDetailsReport',),
    (r'^valuationReport/$', 'valuationReport',),
    (r'^portfolio/$', 'portfolio'),
    (r'^tCBond/$', 'tCBond'),
    (r'^tCSwap/$', 'tCSwap'),
    (r'^identifier/$', 'identifier'),
    (r'^equity/$', 'equity'),    
    (r'^position/$', 'position'),    
    (r'^transaction/$', 'transaction'),    
    (r'^location/$', 'location'),    
    (r'^userProfile/$', 'userProfile'),    
    (r'^positionReport/graph.png/$', 'chartTest',),
    (r'^simpleSlickGrid/$', 'simpleSlickGrid',),
    (r'^admin/lookups/', include(ajax_select_urls)),
    (r'^admin/', include(admin.site.urls)),
    (r'^ajax_select/', include(ajax_select_urls)),
    (r'^TBD/', 'notYetImplemented'),
    (r'^contact/', include('contact_form.urls')),
    (r'^bondCalculator/$', 'bondCalculator',),
    (r'^loadMissingMarketDataForPortfolio/$', 'loadMissingMarketDataForPortfolio',),
    (r'^swapCalculator/$', 'swapCalculator',),
    (r'^assetAllocationGraph/$', 'assetAllocationGraph',),
    (r'^overview/$', 'overview',),
    (r'^performanceReport/$', 'performanceReport',),
    (r'^assetAllocationReport/$', 'assetAllocationReport',),
    (r'^batch/$', 'batch',),
    (r'^netWorthTrendReport/$', 'netWorthTrendReport',),
    (r'^multiBatches/$', 'multiBatches',),
    (r'^javaScriptTest/$','javaScriptTest')
)

urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
) 
