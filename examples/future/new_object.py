'''
Created on Apr 13, 2010

@author: sean
'''

import clyther
from ctypes import c_int

class CLSpam( clyther.device_object ):
    
    
    def __clinit__(self):
        pass
    
    #dynamic device attribute
    x = clyther.device_attribute(c_int, default=0)
    y = clyther.device_attribute(c_int, default=0)
    
    #static python object
    z = 2
    
    
    def add(self):
        return self.x + self.y
#    @clyther.devicemethod
#    def sum(self):
#        pass
#    
#    @clyther.kernelmethod
#    def ksum(self):
#        pass
    

@clyther.task
def devtest( megg ):
    
    x = CLSpam()
    
    z = megg.x
    
def main( ):
    clyther.init()
    eggs = CLSpam( )

    print CLSpam.x

    f1 = devtest.argtypes( CLSpam )
    
    print f1.source
    return  

if __name__ == '__main__':
    main( )
    