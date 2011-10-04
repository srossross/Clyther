'''
Created on Jul 25, 2011

@author: sean
'''
from clyther import kernel, get_global_id, PyKernel
import pyopencl as cl
from ccode.buffer import int_p

PyKernel.use_cache = False

def addX(a, x):

    return a + x

def f1(ff, x):
    return ff(1, x)

gid = get_global_id

i = 1

@kernel()
def do_somthing(a, b):

    idx = get_global_id(0)
    b[idx] = a[idx]
    
    for i in range(10):
        exec """
        uchar16 vec;
        vec[0] = 1;
        break;
        """
    return

def main():
    ctx = cl.Context()

    cladd = do_somthing.compile(ctx, int_p, int_p)

    print cladd.src

if __name__ == '__main__':

    main()

    
# gather resources - recurse through functions and assign types
# close consts -
# expand loops 
# expand structs
# expand slices
