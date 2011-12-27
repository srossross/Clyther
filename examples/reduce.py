'''
Created on Dec 11, 2011

@author: sean
'''
#import clyther as cly
#import clyther.runtime as clrt
#import clyther.array as ca
from clyther.array import CLArrayContext
import opencl as cl
import numpy as np

def main():
    
    ca = CLArrayContext(device_type=cl.Device.GPU)
    
    size = 8
    
    device_input = ca.arange(size)
    
    output = ca.add.reduce(device_input)
    
    print output.item()
    with output.map() as view:
        print "device sum", np.asarray(view).item()


if __name__ == '__main__':
    main()
