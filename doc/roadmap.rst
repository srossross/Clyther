============
Roadmap
============


1.0 Release
-------------

Completed
^^^^^^^^^^^^^^^^^^^

    * Reduce kernel
    * Element-wise kernel
    * U-Funcs 
    * Array indexing
    * CLArray supports 3 dimensions 
    * For loop with 'range' as the iterator 
    * All ctypes as data types including custom Structures
    * Passing a Structure as a scalar argument

Todo
^^^^^^^^^^^^^^^^^^^

    * Add all of the OpenCL runtime functions to the :mod:`clyther.runtime` module.
    * Complete the :class:`clyther.array.CLArray` class:
        * All element wise and reduction operations
        * transpose
        * clip
         
    * Complete Documentation 
    * 90%+ test coverage
    * Improve U-Func performance
    * Array slice operations
    * Add `axis=` option to :func:`clyther.array.reduce` function
    * Pure python emulation context
    * Support builtins:
        * all
        * any
        * min
        * max
        * round
        * zip
        * type
        * isinstance
         
    * Support generator expressions on the host side::
        
        b = ca.gen(x + 1 for x in a)
    
    * Double precision support
        i.e if double is used enable the `cl_khr_fp64` extension
    * Allow returning an array from a function
    * For loops looping over an array
    * Support generator expressions on the device side::
        
        def gen(num):
            for i in range(num):
                yield i**2
       
        @cly.kernel
        def foo(...):
        
            for exp in gen(5):
                 ...
    * Support for builtins like `len` and operator overloading.
    * add the following algorithms:
        * Sort
        * search
        * prefix-sum
        * fft
        * blas routines
     
    
    

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



