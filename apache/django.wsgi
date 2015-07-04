import os, sys
from os.path import dirname

os.environ['DJANGO_SETTINGS_MODULE'] = 'cmt.settings'
sys.path.append('/home/cmt')
sys.path.append('/home/cmt/cmt')
sys.path.append('/home/cmt/cmt/src')
sys.path.append('/usr/local/lib/QuantLib-SWIG-1.1/Python/QuantLib')

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()