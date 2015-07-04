'''
Created on Dec 16, 2012

@author: Capital Market Tools
'''
#from datetime import date
def systemDate(request):
    try:
        systemDate = request.user.get_profile().location.pricingDate
    except:
        systemDate = None
    return {'profileSystemDate': systemDate}

def marketId(request):
    try:
        marketId = request.user.get_profile().marketId
    except:
        marketId = ''
    return {'profileMarketId': marketId}
