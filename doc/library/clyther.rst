:mod:`clyther` --- A python language extention for the OpenCL device  language.
===================================================================================

.. module:: clyther
   :synopsis: A python language extention for the OpenCL device language
.. moduleauthor:: Sean Ross-Ross <srossross@geospin.ca>

.. versionadded:: 1.0


``clyther`` is a python wrapping of openCL in C and requires no extra libraries to install.


.. function:: init( device_type )
    
    `device_type` may be one of the OpenCL defined 'CPU', 'GPU', 'ACCELERATOR', 'ALL', or 'DEFAULT'.
    Or the clyther defined 'EMULATE'.
    
    ``init`` returns a module that containes either the OpenCL runtime library or in the case of 'EMULATE', 
    an emulation runtime library.

..function :: get_context( )

    Returns  the static :class:`copencl.Context` variable initialized by :func:`init`
    
..function :: get_queue( )

    Returns  the static class:`copencl.CommandQueue` variable initialized by :func:`init`


.. function:: kernel( function )
    
    Expose the python function to the OpenCL language.
    The function defined must only contain a subset of the python language and types.
    
    .. note:: 
        
        Working on a definition of this.
    
.. function:: device( function )
    
    Expose the python function to the OpenCL language. This function will not be callable from python.


.. function:: bind( to, value )

    Used as a decorator for kernel functions.
    
    Bind a kernel execution parameter to a value evaluated from the function arguments.
    
    * ``to``: must be one of `global_work_size` or `local_work_size` 
    * ``value``: must be either a string or a function  

.. function:: const( argname )

    Used as a decorator for kernel functions.

    Declare a function argument to be a constant. 
    This will unroll conroll flow statements for faster execution of code.
     
.. function:: const_array_shape( argname )

    Used as a decorator for kernel functions.

    Declare a function argument that must be an array to be have a constant shape and memory layout. 
    This will unroll conroll flow statements for faster execution of code. 

.. class:: DeviceBuffer( shape, ctype , flags=clyther.mem.read_write, context=get_context()  )
    
    More to come...
    
.. class:: Shared( shape, ctype=ctypes.c_char, context=get_context() )
    
    Shared memory. initialization will check that the size of the Shared array will not excceed 
    ``context.devices[0].local_mem_size``, the local memory available to the device.


.. class:: test( )

    run all tests in ``clyther.tests.test_*``.  

