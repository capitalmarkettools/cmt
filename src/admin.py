from models import *
from src.bo.marketData.swaptionVolatilitySurface import SwaptionVolatilitySurface
from src.bo.marketData.swaptionVolatility import SwaptionVolatility

from django.contrib import admin

admin.site.register(Portfolio)
admin.site.register(ModelPosition)
admin.site.register(Location)
admin.site.register(UserProfile)
admin.site.register(Equity)
admin.site.register(HvarConfiguration)
admin.site.register(Identifier)
admin.site.register(TCBond)
admin.site.register(TCSwap)
admin.site.register(InterestRate)
admin.site.register(StockPrice)
admin.site.register(InterestRateCurve)
admin.site.register(Transaction)
admin.site.register(Batch)
admin.site.register(Allocation)
admin.site.register(BondPrice)
admin.site.register(BondOAS)
admin.site.register(SwaptionVolatilitySurface)
admin.site.register(SwaptionVolatility)






