'''
Created on Oct 22, 2011

@author: Capital Market Tools
'''

import numpy as np
from time import time

class Structure(object):
    '''
    IN PROGRESS
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
def driver():
    #The logic below is used for interpolation of 
    #swaption volatility surface
    
    #create five dimensional array with N simulations and M timesteps with curves length M
    
    N = 10000
    M = 360
    bgm = np.zeros(shape=(N,M,M))
#    print 'bgm'
 #   print bgm
    print 'first loop'
    start = time()
    for dim1 in bgm:
  #      print 'dim1'
   #     print dim1
        for dim2 in dim1:
    #        print 'dim2'
     #       print dim2
            for dim3 in dim2:
                pass
      #          print 'dim3'
       #         print dim3
    end = time()
    print 'Execution time ', start - end
    start = time()
    print 'second loop'
    for i in xrange(bgm.shape[0]):
  #      print 'bgm[i]'
   #     print bgm[i]
        for j in xrange(bgm.shape[1]):
    #        print 'bgm[i,j]'
     #       print bgm[i,j]
            for k in xrange(bgm.shape[2]):
      #          print 'bgm[i,j,k]'
       #         print bgm[i,j,k]
                pass
#                bgm[i,j,k] = 2.3
    end = time()
    print 'Execution time ', start - end
    start = time()
    print 'third loop'
    for i in range(bgm.shape[0]):
  #      print 'bgm[i]'
   #     print bgm[i]
        for j in range(bgm.shape[1]):
    #        print 'bgm[i,j]'
     #       print bgm[i,j]
            for k in range(bgm.shape[2]):
      #          print 'bgm[i,j,k]'
       #         print bgm[i,j,k]
                pass
#                bgm[i,j,k] = 2.3
    end = time()
    print 'Execution time ', start - end
    #print bgm
if __name__ == "__main__":
    print 'Start'
    driver()
    print 'End'