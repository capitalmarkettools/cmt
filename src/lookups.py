'''
Created on Jun 8, 2012

@author: Capital Market Tools
'''
from models import Portfolio, Equity, HvarConfiguration

class PortfolioLookup(object):
    def get_query(self,q,request):
        if q == ' ':
            return Portfolio.objects.filter(user=request.user)
        return Portfolio.objects.filter(name__contains=q, user=request.user)

    def format_result(self, p):
        return p.name

    def format_item(self, p):
        return p.name
    
    def get_objects(self, ids):
        return Portfolio.objects.filter(pk__in=ids).order_by('name')

class EquityLookup(object):
    def get_query(self,q,request):
        if q == ' ':
            return Equity.objects.all()
        return Equity.objects.filter(ticker__contains=q)

    def format_result(self, p):
        return p.ticker

    def format_item(self, p):
        return p.ticker
    
    def get_objects(self, ids):
        return Equity.objects.filter(pk__in=ids).order_by('ticker')
    
class HvarConfigLookup(object):
    def get_query(self,q,request):
        if q == ' ':
            return HvarConfiguration.objects.all()
        return HvarConfiguration.objects.filter(name__contains=q)

    def format_result(self, p):
        return p.name

    def format_item(self, p):
        return p.name
    
    def get_objects(self, ids):
        return HvarConfiguration.objects.filter(pk__in=ids).order_by('name')
