from datetime import datetime
# Number of times to indent output
# A list is used to force access by reference
__report_indent = [0]

def log(fn):
    """Decorator to print information about a function
    call for use while debugging.
    Prints function name, arguments, and call number
    when the function is called. Prints this information
    again along with the return value when the function
    returns.
    """
    from django.core.files import File
    from settings import ROOT_PATH
    def wrap(*params,**kwargs):
        call = wrap.callcount = wrap.callcount + 1
        indent = ' ' * __report_indent[0]
        fc = "%s(%s)" % (fn.__name__, ', '.join(
            [a.__repr__() for a in params] +
            ["%s = %s" % (a, repr(b)) for a,b in kwargs.items()]
        ))
        f = open(ROOT_PATH+'/logs/all_logs.txt', 'a')
        file1 = File(f)
        file1.write("XXX%s%s: %s called [#%s]\n" % (indent, datetime.now(), fc, call))
        __report_indent[0] += 1
        ret = fn(*params,**kwargs)
        __report_indent[0] -= 1
        file1.write("XXX%s%s: %s returned %s [#%s]\n" % (indent, datetime.now(), fc, repr(ret), call))
        file1.close()

        return ret
    wrap.callcount = 0
    return wrap

def logShort(fn):
    """Decorator to print information about a function
    call for use while debugging.
    Prints function name, arguments, and call number
    when the function is called. Prints this information
    again along with the return value when the function
    returns.
    """
    from django.core.files import File
    from settings import ROOT_PATH
    def wrap(*params,**kwargs):
        call = wrap.callcount = wrap.callcount + 1

        indent = ' ' * __report_indent[0]
        fc = "%s" % fn.__name__
        f = open(ROOT_PATH+'/logs/all_logs.txt', 'a')
        file1 = File(f)
        file1.write("XXX%s%s: %s called [#%s]\n" % (indent, datetime.now(), fc, call))
        __report_indent[0] += 1
        ret = fn(*params,**kwargs)
        __report_indent[0] -= 1
        file1.write("XXX%s%s: %s returned %s [#%s]\n" % (indent, datetime.now(), fc, repr(ret), call))
        file1.close()

        return ret
    wrap.callcount = 0
    return wrap

