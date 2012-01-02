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
    
    .. seealso:: 
        
        * `NumPy Ufuncs <http://docs.scipy.org/doc/numpy/reference/ufuncs.html>`_

        
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



Exec 
--------

    An non-portable way to generate the exact OpenCL code you want is to use the exec statement::
    
        @cly.global_work_size(lambda a: a.shape)
        @cly.kernel
        def generate_sin(a):
            exec '''
            int gid = clrt.get_global_id(0);
            int n = clrt.get_global_size(0);
            
            float r = (float)gid / (float)n;
            
            // sin wave with 8 oscillations
            float y = r * 16.0f * 3.1415f;
            
            // x is a range from -1 to 1
            a[gid].x = r * 2.0 - 1.0;
            
            # y is sin wave
            a[gid].y = sin(y);

            '''

Compile to OpenCL source
-------------------------

    In this demo we define a kernel but instead of running it we can call the `compile` method with `source_only=True` to get the source::
        
        import opencl as cl
        import clyther as cly
        
        import clyther.runtime as clrt
        
        #Always have to create a context.
        ctx = cl.Context()
        
        @cly.global_work_size(lambda a: [a.size])
        @cly.kernel
        def generate_sin(a):
            
            gid = clrt.get_global_id(0)
            n = clrt.get_global_size(0)
            
            r = cl.cl_float(gid) / cl.cl_float(n)
            
            # sin wave with 8 peaks
            y = r * cl.cl_float(16.0 * 3.1415)
            
            # x is a range from -1 to 1
            a[gid].x = r * 2.0 - 1.0
            
            # y is sin wave
            a[gid].y = clrt.native_sin(y)
        
        
        #===============================================================================
        # Compile to openCL code 
        #===============================================================================
        
        print generate_sin.compile(ctx, a=cl.global_memory(cl.cl_float2), source_only=True) 
        


cl_object
-------------------------


    This example shows that ctype stucts are supported. You will see that the `Foo.bar` method gets compiled and called within the `objects` kernel::
            
        import clyther as cly
        import opencl as cl
        from ctypes import Structure
        from clyther.array import CLArrayContext
        
        class Foo(Structure):
            _fields_ = [('i', cl.cl_float), ('j', cl.cl_float)]
        
            def bar(self):
                return self.i ** 2 + self.j ** 2
            
        @cly.task
        def objects(ret, foo):
            ret[0] = foo.bar()
        
        def main():
            ca = CLArrayContext()  
            
            a = ca.empty([1], ctype='f')
            
            foo = Foo(10., 2.)
             
            objects(ca, a, foo)
            
            print "compiled result: ", a.item().value
            print "python result:   ", foo.bar()
          

.. seealso:: 
    
    * :func:`clyther.global_work_size`
    * :func:`clyther.kernel`
    * :func:`clyther.array.empty`
    
    * Check out the OpenCL api for Event and Queue objects.
    