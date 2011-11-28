:mod:`clyther.runtime` --- OpenCL device language definitions functions and types.
===================================================================================

.. module:: clyther.runtime
   :synopsis: OpenCL device language definitions functions and types.
.. moduleauthor:: Sean Ross-Ross <srossross@geospin.ca>

.. versionadded:: 1.0

``clyther.runtime`` is a python wrapping of openCL in C and requires no extra libraries to install.


.. function:: get_work_dim( )

    Returns the number of dimensions in use.
    
.. function:: get_global_size( dimindx )

    Returns the number of global work-items specified for dimension identified by dimindx.


.. function:: get_global_id( dimindx )

    Returns the unique global work-item ID value for dimension identified by dimindx.

.. function:: get_local_size( dimindx )

    Returns the number of local work-items specified in dimension identified by dimindx.

.. function:: get_local_id( dimindx )

    Returns the unique local work-item ID i.e. a work-item within a 
    specific work-group for dimension identified by dimindx.
    
.. function:: get_num_groups( dimindx )

    Returns the number of work-groups that will execute a kernel for dimension identified by dimindx.

.. function:: get_group_id( dimindx )

    get_group_id returns the work-group ID which is a number from 0 .. get_num_groups(dimindx) –1.


.. function:: barrier( mem_fence_flag )

    All work-items in a work-group executing the kernel on a processor must 
    execute this function before any are allowed to continue execution beyond 
    the barrier. This function must be encountered by all work-items in a 
    work-group executing the kernel.

.. attribute:: CLK_LOCAL_MEM_FENCE

.. attribute:: CLK_GLOBAL_MEM_FENCE




