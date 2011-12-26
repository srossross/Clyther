===============
Examples
===============


Arrays
----------------

This example shows that cl arrays behave as numpy arrays::

    import opencl as cl
    from clyther.array import CLArrayContext
    #Always have to create a context.
    ca = CLArrayContext()
    
    #can print the current devices
    print ca.devices
    
    #Create an array
    a = ca.arange(12)
    
    print a
    
    #map is the same as a memory map
    with a.map() as arr:
        print arr
    
    #can clice
    b = a[1::2]
    
    with b.map() as arr:
        print arr
    
    #ufuncs
    c = a + 1
    
    with c.map() as arr:
        print arr


UFuncs
--------

Ufuncs are also supported::
    
    #Create an array
    a = ca.arange(ctx, 12)
    
    
    @ca.binary_ufunc
    def custom_multuply(x, y):
        '''
        x and y are scalars, custom_multuply will be called for each element an array.
        '''
        return x * (y + 2)
    
    c = custom_multuply(a, a.reshape([12, 1]))
    
    #should be (12, 12)
    print c.shape
    
    with c.map() as arr:
        print arr
        
        
Kernels
--------

    Defining a kernel::
    
        @cly.global_work_size(lambda a: a.shape)
        @cly.kernel
        def generate_sin(a):
            
            gid = clrt.get_global_id(0)
            n = clrt.get_global_size(0)
            
            r = c_float(gid) / c_float(n)
            
            # sin wave with 8 oscillations
            y = r * c_float(16.0 * 3.1415)
            
            # x is a range from -1 to 1
            a[gid].x = r * 2.0 - 1.0
            
            # y is sin wave
            a[gid].y = sin(y)
        
    
    Calling a kernel::
    
        queue = cl.Queue(ca)
        
        a = ca.empty([200], cl.cl_float2)
        
        event = generate_sin(queue, a)
        
        event.wait()



.. seealso:: 
    
    * :func:`clyther.global_work_size`
    * :func:`clyther.kernel`
    * :func:`clyther.array.empty`
    
    * Check out the OpenCL api for Event and Queue objects.
    