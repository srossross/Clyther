.. _tutorial-reduce:
.. highlightlang:: python

*****************************
  CLyther reduce
*****************************

This is an example of a generic OpenCL reduce operator. The arguments include `oper` which may be a python 
function passed to `reduce` at runtime::

    @clyther.kernel
    @clyther.const( 'group_size' )
    @clyther.bind( 'global_work_size', 'group_size' )
    @clyther.bind( 'local_work_size','group_size' )
    def reduce( output, input, shared, oper, group_size=512 ):

        lid = clrt.get_local_id(0)

        gid = clrt.get_group_id(0)
        gsize = clrt.get_num_groups(0)

        gs2 = group_size * 2

        stride = gs2 * gsize

        shared[lid] = 0.0

        i = gid * gs2 + lid

        shared[lid] = 0
        
        while i < input.size:
            shared[lid] = oper( shared[lid], input[i] )
            shared[lid] = oper( shared[lid], input[i+group_size] )
            
            i += stride
            
            clrt.barrier( clrt.K_LOCAL_MEM_FENCE )
        
        for cgs in [ 512 , 256, 128, 64, 32, 16, 8, 4, 2]:
            if group_size >= cgs:
                if lid < cgs/2:
                    shared[lid] = oper( shared[lid], shared[lid + cgs/2] )
                clrt.barrier( clrt.K_LOCAL_MEM_FENCE )
            
        if lid == 0: 
            output[gid] = shared[0]
        

This example shows an *extensible* way to write a reduction operation with CLyther.
In this example notice that the argument `oper` is expected to be a function.


To use this example you may run somthing like::
    
    # where `clarray` is a device array.  
    
    @cl.device
    def add( a,b):
        return a+b

    output = clyther.DeviceBuffer( [1], ctype=clarray.ctype )
    shared = clyther.Shared( ctype=ctypes.c_float )
    
    reduce( output, clarray, shared, add,  group_size=128 )
    
    print output.item( )
    
Walkthrough
============

The first line tells clyther that the python function reduce can now be used as an OpenCL function::
    
    @clyther.kernel

The :func:`clyther.const` decorator tells the CLyther compiler that ``group_size`` is a compile time constant and will unroll controll statements and loops to optimize the performance of the function::

    @clyther.const( 'group_size' )
    
In this function we use :func:`clyther.bind` to ensure that ``global_work_size`` and ``local_work_size`` are the 
correct values and also do not have to be set at each function call::
 
    @clyther.bind( 'global_work_size', 'group_size' )
    @clyther.bind( 'local_work_size','group_size' )


CLyther also comes with a OpenCL :mod:`clyther.runtime` module to expose OpenCL defined constants and functions::

    lid = clrt.get_local_id(0)
    gid = clrt.get_group_id(0)
    gsize = clrt.get_num_groups(0)






