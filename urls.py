from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^', include('cmt.src.urls')),
    (r'^report_builder/',include('report_builder.urls')),
    #by default in django admin goes directly to admin/. Same applies to accounts
	#not sure if this is still needed as we set in settings.py LOGIN_URL
    (r'^admin/',include(admin.site.urls)),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^accounts/profile/$', 'cmt.src.views.logged_in')
)
