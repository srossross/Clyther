
.. highlightlang:: c

.. _opencl_objects:

***************
CLyther C API
***************

These objects and methods are all included with the header ``pyopencl.h``.

the method ``import_opencl( );`` must be called to access all the items defined in ``pyopencl.h``

CLyther Functions
---------------------

.. cfunction:: import_opencl( void )
    
    **Must** be called to initialize API.

.. cfunction:: cl_int CyError( cl_int err );

    Returns 0 on success and 1 if err is not CL_SUCCESS.
    
    example usage ::
    
        ... try opencl call ...
    
        if ( CyError( err) )
        {
            return NULL;
        }
    
CLyther Objects
---------------------

.. ctype:: CyDeviceObject
    
    This subtype of :ctype:`PyObject` represents an ``cl_device_id`` c-type.

.. cvar:: PyTypeObject CyDeviceType
.. cfunction:: int CyDevice_Check( PyObject *o )

    Return true if *o* is of type :cdata:`CyDeviceType` or a subtype of :cdata:`CyDeviceType`.

.. cfunction:: cl_device_id CyDevice_AsDevice( PyObject *o )

.. ctype:: CyContextObject

    This subtype of :ctype:`PyObject` represents an ``cl_context`` c-type.

.. cvar:: PyTypeObject CyContextType
.. cfunction:: int CyContext_Check( PyObject *o )

    Return true if *o* is of type :cdata:`CyContextType` or a subtype of :cdata:`CyContextType`.


.. cfunction:: cl_context CyContext_AsContext( PyObject *o )


.. ctype:: CyProgramObject

    This subtype of :ctype:`PyObject` represents an ``cl_program`` c-type.

.. cvar:: PyTypeObject CyProgramType
.. cfunction:: int CyProgram_Check( PyObject *o )
    
    Return true if *o* is of type :cdata:`CyProgramType` or a subtype of :cdata:`CyProgramType`.
    
.. cfunction:: cl_program CyProgram_AsProgram( PyObject *o )

.. ctype:: CyMemBufferObject

    This subtype of :ctype:`PyObject` represents an ``cl_mem`` c-type.

.. cvar:: PyTypeObject CyMemBufferType
.. cfunction:: int CyMemBuffer_Check( PyObject *o )

    Return true if *o* is of type :cdata:`CyMemBufferType` or a subtype of :cdata:`CyMemBufferType`.
    
.. cfunction:: cl_mem CyMemBuffer_AsMemBuffer( PyObject *o )

.. ctype:: CyEventObject

    This subtype of :ctype:`PyObject` represents an ``cl_event`` c-type.

.. cvar:: PyTypeObject CyEventType
.. cfunction:: int CyEvent_Check( PyObject *o )

    Return true if *o* is of type :cdata:`CyEventType` or a subtype of :cdata:`CyEventType`.

.. cfunction:: cl_event CyEvent_AsEvent( PyObject *o )

.. ctype:: CyKernelObject

    This subtype of :ctype:`PyObject` represents an ``cl_kernel`` c-type.

.. cvar:: PyTypeObject CyKernelType
.. cfunction:: int CyKernel_Check( PyObject *o )

    Return true if *o* is of type :cdata:`CyKernelType` or a subtype of :cdata:`CyKernelType`.
    
.. cfunction:: cl_kernel CyKernel_AsKernel( PyObject *o )

.. ctype:: CyQueueObject

    This subtype of :ctype:`PyObject` represents an ``cl_command_queue`` c-type.

.. cvar:: PyTypeObject CyQueueType
.. cfunction:: int CyQueue_Check( PyObject *o )

    Return true if *o* is of type :cdata:`CyQueueType` or a subtype of :cdata:`CyQueueType`.
    
.. cfunction:: cl_command_queue CyQueue_AsCommandQueue( PyObject *o )

.. ctype:: CyPlatformObject

    This subtype of :ctype:`PyObject` represents an ``cl_platform_id`` c-type.

.. cvar:: PyTypeObject CyPlatformType
.. cfunction:: int CyPlatform_Check( PyObject *o )

    Return true if *o* is of type :cdata:`CyPlatformType` or a subtype of :cdata:`CyPlatformType`.
    
.. cfunction:: cl_platform_id CyPlat_AsPlat( PyObject *o )
            
