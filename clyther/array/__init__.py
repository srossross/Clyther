'''
clyther.array
---------------

The clyther.array module is designed to replicatie the functionality of numpy 
for OpenCL memory objects.

the main entry point into this module is the :class:`CLArrayContext` class.

The end goal is to seamlessly be able to switch between OpenCL and numpy.

Where you would write::

    import numpy as np
    
    a = np.arange(0, 10.)
    
To specify a GPU array you would write::

    import opencl as cl
    from clyther.array import CLArrayContext
    
    ca = CLArrayContext(device_type=cl.Device.GPU)
    
    a = ca.arange(0, 10.)
    

'''
from blitz import blitz
from ufuncs import add, multiply, sin
from ufunc_framework import binary_ufunc

from functions import arange, empty, empty_like, setslice

    
from clarray import CLArray

from clyther.array.reduce_array import reduce

from clyther.array.array_context import CLArrayContext

