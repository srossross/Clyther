'''
Created on Dec 7, 2011

@author: sean
'''
from clyther.array.ufunc_framework import binary_ufunc, unary_ufunc
import clyther.runtime as clrt 
from clyther.array.array_context import CLArrayContext

@CLArrayContext.func('add')
@binary_ufunc
def add(a, b):
    return a + b

sum = CLArrayContext.func("sum")(add.reduce)

@CLArrayContext.func('multiply')
@binary_ufunc
def multiply(a, b):
    return a * b

@unary_ufunc
def cly_sin(x):
    return clrt.sin(x)

sin = cly_sin

def main():
    import opencl as cl
    from clyther.array.functions import arange, linspace
    import numpy as np
    
    ctx = cl.Context()
    a = arange(ctx, 12.0,ctype='(2)f')
#    a = linspace(ctx, 0, 12, 12)
    
    
    with a.map() as arr:
        print arr
    
    b = a + 1
    
    with b.map() as arr:
        print arr
        
    c = sin(b)
    
    with c.map() as arr, b.map() as barr:
        
        print arr
        print np.sin(barr)
        
        
        
if __name__ == '__main__':
    main()
