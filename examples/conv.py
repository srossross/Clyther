'''
Created on Dec 7, 2011

@author: sean
'''
import clyther as cly
import clyther.runtime as clrt
import opencl as cl
from ctypes import c_float

'''
@kernel
@bind('global_work_size','a.size/512')
@bind('local_work_size', 512)
def conv(a,b,ret):
    
    i = clrt.get_global_id(0)
    
    w = (b.size-1)/2
    
    start = 0 if (i < w) else i-w
    stop = a.size if (i+w >= a.size) else i+w+1 
    
    sum = 0.
    for k in range(start,stop):
        sum += a[k] * b[k+w-i]
        
    ret[i] = sum
'''
@cly.global_work_size(lambda a, b, ret: a.size // 512)
@cly.local_work_size([512])
@cly.kernel
def conv(a, b, ret):
    
    i = clrt.get_global_id(0)
    
    w = (b.size-1)/2
    
    start = 0 if (i < w) else i-w
    stop = a.size if (i+w >= a.size) else i+w+1 
    
    sum = c_float(0.)
    
    for k in range(start,stop):
        sum += a[k] * b[k+w-i]
        
    ret[i] = sum
        
def main():
    
    ctx = cl.Context(device_type=cl.Device.CPU)

    source_only=False
    source = conv.compile(ctx, a=cl.global_memory(c_float), 
                          b=cl.global_memory(c_float), 
                          ret=cl.global_memory(c_float),
                          source_only=source_only)
    
    source.program
    print source

if __name__ == '__main__':
    main()
