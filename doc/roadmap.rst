============
Roadmap
============


1.0 Release
-------------

    * Add all of the OpenCL runtime functions to the :mod:`clyther.runtime` module.
    * Complete the :class:`clyther.array.CLArray` class. 
    * Complete Documentation 
    * 90%+ test coverage
    
    .. TODO:: Think about the 1.0 goals 

Possible Extensions
-------------------------

New Context Types
^^^^^^^^^^^^^^^^^^^

I think it would be great to have multiple context types. clyther tasks and kerenels could be compiled to support a specific context. 
Contexts would allow experimentation without changeing the algorithm Ideally the following code would work with any context::
    
   @binary_ufunc
   def add(a, b):
       return a + b
    
   # Create a context. this part would change
   ca = cly.array.CLArrayContext() 
   
   a = ca.arange(100)
   
   b = add(a, 2)
    
   print add.reduce(b)

   
Some contexts that may be useful include:

NumpyContext:
    This would be the default context. All tasks would be compiled into C functions. Kernels would not be supported. 

OpenMPContext:
    There is an excellent opportunity to use OpenMP. I have found that it is hard to create fast vectorized operations in OpenCL 
    (e.g. `y[:,10] = a + b + c[:1]`) perhaps we could compile to C and parallelize loops using OpenMP.

RemoteContext:
    Connect to one or many remote machines to run the algorithm. (possibly using pycloud)

CLEmulation context:
    Run all the tasks and kernels in Python for easy debugging.

Cython context:
    JIT Compile to Cython 
    
    
Investigate `Copperhead <http://code.google.com/p/copperhead/>`_
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    
It would be great to start talking with the copperhead team.

