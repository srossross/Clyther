:mod:`copencl` --- A python wrapper for the C OpenCL library.
=============================================================

.. module:: copencl
   :synopsis: A python wrapper for the C OpenCL library.
.. moduleauthor:: Sean Ross-Ross <srossross@geospin.ca>

.. versionadded:: 1.0


``copencl`` is a python wrapping of openCL in C and requires no extra libraries to install.


.. function:: get_platforms( )

    Returns the list of platforms available can be obtained using the following function.
    
.. function:: get_devices( device_type )

    Returns the list of devices available on a platform can be obtained using the following function.
    
    `device_type` may be one of 'ALL','CPU', 'GPU', 'ACCELERATOR','DEFAULT'

Platform Object
----------------------

.. class:: Platform( )
    The Platform class has no constructor and must be gotten from :func:`GetPlatformIDs`
    
    
    .. method:: get_devices( )
    
        returns a list of devices available on this platform.
    
    .. attribute:: profile
        
        OpenCL profile string. 
        Returns the profile name supported by the implementation. The profile name returned can be one of the following strings:
        `FULL_PROFILE`  or `EMBEDDED_PROFILE` 

        
    .. attribute:: version


        Returns the OpenCL version supported by the implementation.

        The `major_version.minor_version`
    
    .. attribute:: name
    
        Platform name.

    .. attribute:: vendor

        Platform vendor.

    .. attribute:: extensions

        Returns a space separated list of extension names (the extension names themselves do not contain any spaces) 
        supported by the platform. 
        Extensions defined here must be supported by all devices associated with this platform.
    
Device Object
----------------------

.. class:: Device( )
    
    The Platform class has no constructor and must be gotten from a :class:`Platform` class or the function :func:`get_devices`
    
    .. attribute:: type
    
        The OpenCL device type.
        
    .. attribute:: vendor_id
    
        A unique device vendor identifier.
    
    .. attribute:: max_compute_units
        
        The number of parallel compute cores on the OpenCL device. The minimum value is 1.
        
        
    .. attribute:: max_work_item_dimentions
        
        Maximum dimensions that specify the global and local work-item IDs used by the data parallel execution model. 
        The minimum value is 3.
        
    .. attribute:: max_work_item_sizes
    
        Maximum number of work-items that can be specified in 
        each dimension of the work-group to :class:`Kernel`.
    
    .. attribute:: max_work_group_size
        
        Maximum number of work-items in a work-group executing a kernel using the data parallel execution model.
    
    .. attribute:: max_clock_frequency
    
        Maximum configured clock frequency of the device in MHz.
        
    .. attribute:: address_bits
        
        The default compute device address space size specified as an unsigned 
        integer value in bits. Currently supported values are 32 or 64 bits.

    .. attribute:: max_mem_alloc_size
    
        Max size of memory object allocation in bytes. 
    
    .. attribute:: max_parameter_size
    
        Max size in bytes of the arguments that can be passed to a kernel. 
        
        The minimum value is 256.
        
    .. attribute:: mem_base_addr_align
    
        Describes the alignment in bits of the base address of any allocated memory object.
        
    .. attribute:: min_data_type_align_size
    
        The smallest alignment in bytes which can be used for any data type.
        
    .. attribute:: global_mem_size
    
        Size of global device memory in bytes.
    
    .. attribute:: max_constant_buffer_size
    
        Max size in bytes of a constant buffer allocation. The minimum value is 64 KB.
    
    .. attribute:: max_constant_args
    
        Max number of arguments declared with the __constant qualifier in a kernel. The minimum value is 8.
        
    .. attribute:: local_mem_size
    
        Size of local memory arena in bytes. 
        
        The minimum value is 16 KB.
        
        
    .. attribute:: endian_little
    
        If  the OpenCL device is a little endian device.
        
    .. attribute:: available
    
        If the device is available.
    
    .. attribute:: name
    
        Device name

    .. attribute:: vendor
    
        Vendor name
        
    .. attribute:: driver_version
    
        OpenCL software driver version string in the form major_number.minor_number.
        
    .. attribute:: profile
    
        OpenCL profile
        
    .. attribute:: version
    
        OpenCL version string. Returns the OpenCL version supported by the device.
        
    .. attribute:: extensions
    
        Returns a space separated string of extension names.
        
        
Program Object
----------------------

.. class:: Program( context, source )

    An OpenCL program consists of a set of kernels that are identified 
    as functions declared with the ``__kernel`` 
    qualifier in the program source. 
    OpenCL programs may also contain auxiliary functions and constant 
    data that can be used by ``__kernel`` functions. 
    The program executable can be generated online or offline by the 
    OpenCL compiler for the appropriate target device(s).


    .. attribute:: Program.source
        
        The source code of the program.
        
    .. method:: Program.build_status( device )
    
        Returns the build status of program for a specific device as given by device.
    
    .. method:: Program.build_log( device )
    
        Return the build log when Program.build was called for device.
        
    .. method:: Program.build( devices [, options ] )

        Builds (compiles & links) a program executable from the program source
        or binary for all the devices or a specific device(s) in the OpenCL 
        context associated with program. OpenCL allows program executables to be 
        built using the source or the binary.

Kernel Object
----------------------

.. class:: Kernel( program, kernel_name )

    A kernel is a function declared in a program. 
    A kernel is identified by the ``__kernel`` qualifier applied to any function in a program. 
    A kernel object encapsulates the specific ``__kernel``
    function declared in a program and the argument values to be used when executing this ``__kernel``
    function.
        
    .. method:: set_arg( index , size, value )
    
        To execute a kernel, the kernel arguments must be set.
        
    .. method:: get_work_group_size( device )
    .. method:: get_compile_work_group_size( device )
    .. method:: get_local_mem_size( device )
    
        
    .. attribute:: name
        
        Kernel name
        
    .. attribute:: num_args
    
        Return the number of arguments to kernel.
        


Context Object
----------------------

.. class:: Context( )
    
    An OpenCL context is created with one or more devices. 
    Contexts are used by the OpenCL runtime for managing objects 
    such as command-queues, memory, program and kernel objects 
    and for executing kernels on one or more devices specified 
    in the context.

    .. attribute:: devices
    
        returns the devices associated with this context.
      

CommandQueue Object
----------------------
  
.. class:: CommandQueue

    OpenCL objects such as memory, program and kernel objects are 
    created using a context. Operations on these objects are 
    performed using a command-queue. The command-queue can be used 
    to queue a set of operations (referred to as commands) in 
    order. Having multiple command-queues allows applications 
    to queue multiple independent commands without requiring 
    synchronization. Note that this should work as long as these 
    objects are not being shared. Sharing of objects across 
    multiple command-queues will require the application to 
    perform appropriate synchronization.

    .. attribute:: profile_enabled
    
        Enable or disable profiling of commands in the command-queue. 
        
    .. attribute:: out_of_order_exec_mode_enabled
        
        Determines whether the commands queued in the command-queue are 
        executed in-order or out-of- order. If set, the commands in 
        the command-queue are executed out-of-order. Otherwise, 
        commands are executed in-order.
    
    .. method:: enqueue_kernel( kernel, global_work_size, local_work_size, event_wait_list )
        
        enqueues a command to execute a kernel on a device.
        
    .. method:: enqueue_read_buffer(  )
        
        
    .. method:: enqueue_write_buffer(  )
    
        
    .. method:: enqueue_native_kernel(  )
        
        enqueues a command to execute a native C/C++/Python function not compiled using the OpenCL compiler.
        
    .. method:: flush(  )
    
        Issues all previously queued OpenCL commands in command_queue 
        to the device associated with command_queue. flush only guarantees 
        that all queued commands to command_queue get issued to the appropriate device. 
        There is no guarantee that they will be complete after flush returns.
        
    .. method:: finish(  )
    
        Blocks until all previously queued OpenCL commands in command_queue are issued to the 
        associated device and have completed. finish does not return until all queued commands 
        in command_queue have been processed and completed. finish is also a 
        synchronization point.


MemBuffer Object
----------------------
    
.. class:: MemBuffer( context, flags, size [,host_ptr] )
    
    A buffer object stores a one-dimensional collection of elements.
    
    .. attribute:: size
    
        This size of the buffer in bytes.
        
    .. attribute:: flags
        
        
        
    .. attribute:: context

Event Object
----------------------

.. class:: Event( )

    .. attribute:: type 
           
    .. attribute:: status

    .. method wait( )
        
        Wait for event to complete.
    

:mod:`copencl.MEM` --- Flags for memory allocation 
=============================================================

.. module:: copencl.MEM
   :synopsis: Flags for memory allocation
.. moduleauthor:: Sean Ross-Ross <srossross@geospin.ca>

.. versionadded:: 1.0


.. data:: READ_WRITE

    This flag specifies that the memory object will be read and written by a kernel. 
    This is the default.
    
.. data:: WRITE_ONLY
    
    This flags specifies that the memory object will be written but not read by a kernel.
    Reading from a buffer or image object created with ``WRITE_ONLY`` inside a kernel is undefined.
    
.. data:: READ_ONLY

    This flag specifies that the memory object is a read-only memory object when used inside a kernel.
    Writing to a buffer or image object created with ``READ_ONLY`` inside a kernel is undefined.
    
.. data:: USE_HOST_PTR

    This flag is valid only if host_ptr is not NULL. If specified, 
    it indicates that the application wants the OpenCL implementation 
    to use memory referenced by host_ptr as the storage bits for the memory object.
    OpenCL implementations are allowed to cache the buffer contents
    pointed to by host_ptr in device memory. This cached copy can
    be used when kernels are executed on a device.
    
.. data:: ALLOC_HOST_PTR

    This flag specifies that the application wants the OpenCL 
    implementation to allocate memory from host accessible memory.
    
.. data:: COPY_HOST_PTR

    This flag is valid only if host_ptr is not NULL. If specified, 
    it indicates that the application wants the OpenCL implementation to 
    allocate memory for the memory object and copy the data from memory referenced by host_ptr.
    
    ``COPY_HOST_PTR`` and ``USE_HOST_PTR`` are mutually exclusive.
    ``COPY_HOST_PTR`` can be used with ``ALLOC_HOST_PTR`` to initialize 
    the contents of the cl_mem object allocated using host-accessible (e.g. PCIe) memory.
        
        
:mod:`copencl.COMMAND` --- Flags polling command type 
=============================================================

.. module:: copencl.COMMAND
   :synopsis: Flags
.. moduleauthor:: Sean Ross-Ross <srossross@geospin.ca>

.. versionadded:: 0.1

.. data:: NDRANGE_KERNEL
.. data:: TASK
.. data:: NATIVE_KERNEL
.. data:: NATIVE_KERNEL
.. data:: READ_IMAGE
.. data:: READ_IMAGE
.. data:: COPY_IMAGE
.. data:: COPY_BUFFER_TO_IMAGE
.. data:: COPY_IMAGE_TO_BUFFER

.. data:: MAP_BUFFER
.. data:: MAP_IMAGE
.. data:: UNMAP_MEM_OBJECT

.. data:: MARKER
.. data:: ACQUIRE_GL_OBJECTS
.. data:: RELEASE_GL_OBJECTS


:mod:`copencl.QUEUE` --- Flags setting and getting queue properties 
===================================================================

.. module:: copencl.QUEUE
   :synopsis: Flags
.. moduleauthor:: Sean Ross-Ross <srossross@geospin.ca>

.. versionadded:: 0.1


.. data:: OUT_OF_ORDER_EXEC_MODE_ENABLE
.. data:: PROFILING_ENABLE


:mod:`copencl.DEVICE_TYPE` --- Flags setting and getting device types 
==========================================================================

.. module:: copencl.DEVICE_TYPE
   :synopsis: Flags
.. moduleauthor:: Sean Ross-Ross <srossross@geospin.ca>

.. versionadded:: 0.1


.. data:: ALL
.. data:: CPU
.. data:: GPU
.. data:: ACCELERATOR
.. data:: DEFAULT


:mod:`copencl.EXEC` --- Flags device execution capabilities 
=============================================================

.. module:: copencl.EXEC
   :synopsis: Flags
.. moduleauthor:: Sean Ross-Ross <srossross@geospin.ca>

.. versionadded:: 0.1


.. data:: KERNEL
.. data:: NATIVE_KERNEL

:mod:`copencl.MAP` --- Flags for memory allocation 
=============================================================

.. module:: copencl.MAP
   :synopsis: Flags
.. moduleauthor:: Sean Ross-Ross <srossross@geospin.ca>

.. versionadded:: 0.1

.. data:: READ
.. data:: WRITE
