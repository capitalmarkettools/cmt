from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from src.bo.Enum import Currency, Frequency, Roll, TimePeriod, Index, PositionType, TransactionType
from src.bo.static import Calendar
from src.bo import cmt, Shift, Enum, Date, ErrorHandling, VARUtilities
from src.bo.decorators import log
from src.models import BondOAS, TCBond

print 'Start'
f = Date.Date(day=25,month=7,year=2013)
l = Date.Date(day=18,month=9,year=2013)
from src.bo import VARUtilities
timeSteps = VARUtilities.VARTimePeriodsAndSteps()
timeSteps.generate(start=f, end=l, num=1, term=TimePeriod('D'), calendar=Calendar.US())
for timeStep in timeSteps.timeSteps:
    bondOAS = BondOAS(tCBond=TCBond.objects.get(name='PortAuth_4.00_JAN42'), 
                      pricingDate=timeStep,marketId='EOD',mid=0.014)
    bondOAS.save()
print 'End'