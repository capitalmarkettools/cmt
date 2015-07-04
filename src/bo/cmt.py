'''
Created on Nov 26, 2011

@author: Capital Market Tools
'''

class cmt(object):
    '''
    Top level class every object is inherited from
    Tests do not use this class
    '''
    def __init__(self):
        '''
        Constructor
        '''
    def removeXMLBreaks(self, string):
        string = string.replace('<','')
        string = string.replace('>','')
        return string
     
    def __str__(self):
        s = "<class><className>" + object.__class__.__name__
        s += "</className><data>"
        for attr, value in self.__dict__.iteritems():
            s = s + str(attr) + ">" + self.removeXMLBreaks(str(value))
            s = s + "</" + str(attr) + ">"
        s = s + "</data></class>" 
        return s
    
    def dump(self):
        s = "<class><className>" + object.__class__.__name__
        s += "</className><data>"
        for attr, value in self.__dict__.iteritems():
            s = s + str(attr) + ">" + self.removeXMLBreaks(str(value))
            s = s + "</" + str(attr) + ">"
        s = s + "</data></class>" 
        return s
