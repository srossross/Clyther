'''

'''
import weakref
import struct
import ctypes
from _cl cimport * 
from libc.stdio cimport printf

from libc.stdlib cimport malloc, free 
from cpython cimport PyObject, Py_DECREF, Py_INCREF, PyBuffer_IsContiguous, PyBuffer_FillContiguousStrides
from cpython cimport Py_buffer, PyBUF_SIMPLE, PyBUF_STRIDES, PyBUF_ND, PyBUF_FORMAT, PyBUF_INDIRECT, PyBUF_WRITABLE

from opencl.types_formats import refrence, ctype_from_format, type_format, cdefn
from inspect import isfunction

cdef extern from "Python.h":

    object PyByteArray_FromStringAndSize(char * , Py_ssize_t)
    object PyMemoryView_FromBuffer(Py_buffer * info)
    int PyObject_GetBuffer(object obj, Py_buffer * view, int flags)
    int PyObject_CheckBuffer(object obj)
    void PyBuffer_Release(Py_buffer * view)
    void PyEval_InitThreads()

MAGIC_NUMBER = 0xabc123

    
PyEval_InitThreads()

all_opencl_errors = {
CL_SUCCESS: 'CL_SUCCESS',
CL_INVALID_VALUE: 'CL_INVALID_VALUE',
CL_INVALID_BINARY: 'CL_INVALID_BINARY',
CL_INVALID_BUFFER_SIZE: 'CL_INVALID_BUFFER_SIZE',
CL_INVALID_BUILD_OPTIONS: 'CL_INVALID_BUILD_OPTIONS',
CL_INVALID_CONTEXT: 'CL_INVALID_CONTEXT',
CL_INVALID_DEVICE: 'CL_INVALID_DEVICE',
CL_INVALID_EVENT: 'CL_INVALID_EVENT',
CL_INVALID_HOST_PTR: 'CL_INVALID_HOST_PTR',
CL_INVALID_KERNEL_NAME: 'CL_INVALID_KERNEL_NAME',
CL_INVALID_OPERATION: 'CL_INVALID_OPERATION',
CL_INVALID_KERNEL_NAME: 'CL_INVALID_KERNEL_NAME',
CL_INVALID_COMMAND_QUEUE: 'CL_INVALID_COMMAND_QUEUE',
CL_INVALID_CONTEXT: 'CL_INVALID_CONTEXT',
CL_INVALID_MEM_OBJECT: 'CL_INVALID_MEM_OBJECT',
CL_INVALID_EVENT_WAIT_LIST: 'CL_INVALID_EVENT_WAIT_LIST',
CL_INVALID_PROPERTY: 'CL_INVALID_PROPERTY',
CL_INVALID_DEVICE_TYPE: 'CL_INVALID_DEVICE_TYPE',
CL_INVALID_PROGRAM: 'CL_INVALID_PROGRAM',
CL_INVALID_PROGRAM_EXECUTABLE: 'CL_INVALID_PROGRAM_EXECUTABLE',
CL_INVALID_PLATFORM: 'CL_INVALID_PLATFORM',
CL_INVALID_KERNEL: 'CL_INVALID_KERNEL',
CL_INVALID_KERNEL_ARGS: 'CL_INVALID_KERNEL_ARGS',
CL_INVALID_WORK_DIMENSION: 'CL_INVALID_WORK_DIMENSION',
CL_INVALID_GLOBAL_WORK_SIZE: 'CL_INVALID_GLOBAL_WORK_SIZE',
CL_INVALID_GLOBAL_OFFSET: 'CL_INVALID_GLOBAL_OFFSET',
CL_INVALID_WORK_GROUP_SIZE: 'CL_INVALID_WORK_GROUP_SIZE',
CL_INVALID_WORK_ITEM_SIZE: 'CL_INVALID_WORK_ITEM_SIZE',
CL_INVALID_IMAGE_SIZE: 'CL_INVALID_IMAGE_SIZE',
CL_INVALID_ARG_INDEX: 'CL_INVALID_ARG_INDEX',
CL_INVALID_ARG_VALUE: 'CL_INVALID_ARG_VALUE',
CL_INVALID_SAMPLER: 'CL_INVALID_SAMPLER',
CL_INVALID_ARG_SIZE: 'CL_INVALID_ARG_SIZE',
CL_INVALID_KERNEL_DEFINITION: 'CL_INVALID_KERNEL_DEFINITION',
CL_MISALIGNED_SUB_BUFFER_OFFSET: 'CL_MISALIGNED_SUB_BUFFER_OFFSET',
CL_MEM_OBJECT_ALLOCATION_FAILURE: 'CL_MEM_OBJECT_ALLOCATION_FAILURE',
CL_DEVICE_NOT_AVAILABLE: 'CL_DEVICE_NOT_AVAILABLE',
CL_COMPILER_NOT_AVAILABLE: 'CL_COMPILER_NOT_AVAILABLE',
CL_BUILD_PROGRAM_FAILURE: 'CL_BUILD_PROGRAM_FAILURE',
CL_INVALID_OPERATION: 'CL_INVALID_OPERATION',
CL_OUT_OF_HOST_MEMORY: 'CL_OUT_OF_HOST_MEMORY',
CL_OUT_OF_RESOURCES: 'CL_OUT_OF_RESOURCES',
CL_DEVICE_NOT_FOUND: 'CL_DEVICE_NOT_FOUND',
CL_EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST: 'CL_EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST',
}

OpenCLErrorStrings = {
                
    CL_INVALID_CONTEXT: 'Context is not a valid context.',
    CL_INVALID_BUFFER_SIZE: 'size is 0',
    
    CL_INVALID_EVENT:'Event objects specified in event_list are not valid event objects',
    
    CL_INVALID_HOST_PTR : '''if host_ptr is NULL and CL_MEM_USE_HOST_PTR or  
CL_MEM_COPY_HOST_PTR are set in flags or if host_ptr is not NULL but 
CL_MEM_COPY_HOST_PTR or CL_MEM_USE_HOST_PTR are not set in flags.''',
    CL_MEM_OBJECT_ALLOCATION_FAILURE :"There is a failure to allocate memory for buffer object.",
    CL_OUT_OF_RESOURCES : "There is a failure to allocate resources required by the OpenCL implementation on the device.",
    CL_OUT_OF_HOST_MEMORY : "There is a failure to allocate resources required by the OpenCL implementation on the host",
    CL_INVALID_PROGRAM :'Program is not a valid program object.',
    CL_INVALID_VALUE: 'CL_INVALID_VALUE: this one should have been caught by python!',
    CL_INVALID_DEVICE : 'OpenCL devices listed in device_list are not in the list of devices associated with program.',
    CL_INVALID_BINARY:  'program is created with clCreateWithProgramBinary and devices listed in device_list do not have a valid program binary loaded.',
    CL_INVALID_BUILD_OPTIONS :'The build options specified by options are invalid.',
    CL_INVALID_OPERATION: 'The build of a program executable for any of the devices listed in device_list by a previous call to clBuildProgram for program has not  completed.',
    CL_COMPILER_NOT_AVAILABLE: 'Program is created with clCreateProgramWithSource and a compiler is not available' ,
    CL_BUILD_PROGRAM_FAILURE: '''if there is a failure to build the program executable.  
This error will be returned if clBuildProgram does not return until the build has 
completed. 
''',
    CL_INVALID_OPERATION: 'There are kernel objects attached to program.',
    CL_OUT_OF_HOST_MEMORY : 'if there is a failure to allocate resources required by the OpenCL implementation on the host.',
    
    CL_EXEC_STATUS_ERROR_FOR_EVENTS_IN_WAIT_LIST: 'The execution status of any of the events in event_list is a negative integer value',
    
    CL_INVALID_PROGRAM_EXECUTABLE : 'there is no successfully built executable for program',
    
    CL_INVALID_KERNEL_NAME : ' kernel_name is not found in program.',
    
    CL_INVALID_KERNEL_DEFINITION : ('The function definition for __kernel  function ' 
                                    'given by kernel_name such as the number of arguments, the argument types are not the' 
                                    'same for all devices for which the program executable has been built'),
                }


class OpenCLException(Exception):
    def __init__(self, err_code, mapping=None):
        if mapping is None:
            mapping = OpenCLErrorStrings
        Exception.__init__(self, err_code, all_opencl_errors.get(err_code,'CL_ERROR'), mapping.get(err_code, 'Uknown OpenCL error'))

cpdef get_platforms():
    '''
    '''
    cdef cl_uint num_platforms
    cdef cl_platform_id plid
    
    ret = clGetPlatformIDs(0, NULL, & num_platforms)
    if ret != CL_SUCCESS:
        raise OpenCLException(ret)
    cdef cl_platform_id * cl_platform_ids = < cl_platform_id *> malloc(num_platforms * sizeof(cl_platform_id *))
    
    ret = clGetPlatformIDs(num_platforms, cl_platform_ids, NULL)
    
    if ret != CL_SUCCESS:
        free(cl_platform_ids)
        raise OpenCLException(ret)
    
    platforms = []
    for i in range(num_platforms):
        plat = Platform()
        plat.platform_id = cl_platform_ids[i]
        platforms.append(plat)
        
    free(cl_platform_ids)
    return platforms
    

cdef class Platform:

    cdef cl_platform_id platform_id
    
    def __cinit__(self):
        pass
    
    def __repr__(self):
        return '<opencl.Platform name=%r profile=%r>' % (self.name, self.profile,)

    
    cdef get_info(self, cl_platform_info info_type):
        cdef size_t size
        cdef cl_int err_code
        err_code = clGetPlatformInfo(self.platform_id,
                                   info_type, 0,
                                   NULL, & size)
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
        cdef char * result = < char *> malloc(size * sizeof(char *))
        
        err_code = clGetPlatformInfo(self.platform_id,
                                   info_type, size,
                                   result, NULL)
        
        if err_code != CL_SUCCESS:
            free(result)
            raise OpenCLException(err_code)
        
        cdef bytes a_python_byte_string = result
        free(result)
        return a_python_byte_string

    property profile:
        def __get__(self):
            return self.get_info(CL_PLATFORM_PROFILE)

    property version:
        def __get__(self):
            return self.get_info(CL_PLATFORM_VERSION)

    property name:
        def __get__(self):
            return self.get_info(CL_PLATFORM_NAME)

    property vendor:
        def __get__(self):
            return self.get_info(CL_PLATFORM_VENDOR)

    property extensions:
        def __get__(self):
            return self.get_info(CL_PLATFORM_EXTENSIONS)

    def  devices(self, cl_device_type dtype=CL_DEVICE_TYPE_ALL):

        cdef cl_int err_code
           
        cdef cl_uint num_devices
        err_code = clGetDeviceIDs(self.platform_id, dtype, 0, NULL, & num_devices)
            
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
        cdef cl_device_id * result = < cl_device_id *> malloc(num_devices * sizeof(cl_device_id *))
        
        err_code = clGetDeviceIDs(self.platform_id, dtype, num_devices, result, NULL)
        
        devices = []
        for i in range(num_devices):
            device = Device()
            device.device_id = result[i]
            devices.append(device)
            
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
        return devices
        
cdef class Device:
    DEFAULT = CL_DEVICE_TYPE_DEFAULT
    ALL = CL_DEVICE_TYPE_ALL
    CPU = CL_DEVICE_TYPE_CPU
    GPU = CL_DEVICE_TYPE_GPU
    
    cdef cl_device_id device_id

    def __cinit__(self):
        pass
    
    def __repr__(self):
        return '<opencl.Device name=%r type=%r>' % (self.name, self.device_type,)
    
    def __hash__(Device self):
        
        cdef size_t hash_id = < size_t > self.device_id

        return int(hash_id)
    
    def __richcmp__(Device self, other, op):
        
        if not isinstance(other, Device):
            return NotImplemented
        
        if op == 2:
            return self.device_id == (< Device > other).device_id
        else:
            return NotImplemented
            
            
             
    property device_type:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_device_type dtype
            
            
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_TYPE, sizeof(cl_device_type), < void *>& dtype, NULL)
                
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return dtype

    property has_image_support:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_bool result
            
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_IMAGE_SUPPORT, sizeof(cl_bool), < void *>& result, NULL)
                
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return True if result else False
    

    property name:
        def __get__(self):
            cdef size_t size
            cdef cl_int err_code
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_NAME, 0, NULL, & size)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            cdef char * result = < char *> malloc(size * sizeof(char *))
            
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_NAME, size * sizeof(char *), < void *> result, NULL)

            if err_code != CL_SUCCESS:
                free(result)
                raise OpenCLException(err_code)
            
            cdef bytes a_python_byte_string = result
            free(result)
            return a_python_byte_string

    property native_kernel:

        def __get__(self):
            cdef size_t size
            cdef cl_int err_code
            cdef cl_device_exec_capabilities result
            
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_EXECUTION_CAPABILITIES, sizeof(cl_device_exec_capabilities), & result, NULL)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            
            return True if result & CL_EXEC_NATIVE_KERNEL else False 


cdef class ContextProperties:

    cdef cl_platform_id platform_id
    cdef size_t _gl_context
    cdef size_t _gl_sharegroup
    
    def __cinit__(self):
        self.platform_id = NULL
        self.gl_context = 0
        self._gl_sharegroup = 0
        
    property platform:
        def __get__(self):
            if self.platform_id != NULL:
                return clPlatformAs_PyPlatform(self.platform_id)
            else:
                return None

        def __set__(self, Platform value):
            self.platform_id = clPlatformFromPyPlatform(value)

    property gl_context:
        def __get__(self):
            return self._gl_context

        def __set__(self, value):
            self._gl_context = value
            
    property gl_sharegroup:
        def __get__(self):
            return self._gl_sharegroup

        def __set__(self, value):
            self._gl_sharegroup = value
    
    @classmethod
    def get_current_opengl_context(cls):
        return < size_t > CGLGetCurrentContext()

    @classmethod
    def get_current_opengl_sharegroup(cls):
        return < size_t > CGLGetShareGroup(< void *> CGLGetCurrentContext())
        
    def as_dict(self):
        nprops = 0
        
        if self.platform_id != NULL:
            nprops += 1
        if self._gl_context != 0:
            nprops += 1
        if self._gl_context != 0:
            nprops += 1
            
        props = {}
           
        if self.platform_id != NULL:
             props[ < size_t > CL_CONTEXT_PLATFORM] = < size_t > self.platform_id
        if self._gl_sharegroup != 0:
             props[ < size_t > CL_CONTEXT_PROPERTY_USE_CGL_SHAREGROUP_APPLE] = < size_t > self._gl_sharegroup
        
        props[nprops * 2] = None
        
        return props
    
        
    cdef cl_context_properties * context_properties(self):
        
        nprops = 0
        cdef cl_context_properties * props = NULL
        
        if self.platform_id != NULL:
            nprops += 1
        if self._gl_context != 0:
            nprops += 1
        if self._gl_sharegroup != 0:
            nprops += 1
            
        if nprops > 0:
            props = < cl_context_properties *> malloc(sizeof(cl_context_properties) * (1 + 2 * nprops))
           
        cdef count = 0
        if self.platform_id != NULL:
             props[count] = CL_CONTEXT_PLATFORM
             count += 1
             props[count] = < cl_context_properties > self.platform_id
             count += 1

        if self._gl_context != 0:
             props[count] = < cl_context_properties > CL_CONTEXT_PROPERTY_USE_CGL_SHAREGROUP_APPLE
             count += 1
             props[count] = < cl_context_properties > self._gl_context
             count += 1
             
        if self._gl_sharegroup != 0:
             props[count] = < cl_context_properties > CL_CONTEXT_PROPERTY_USE_CGL_SHAREGROUP_APPLE
             count += 1
             props[count] = < cl_context_properties > self._gl_sharegroup
             count += 1
             
        props[count] = < cl_context_properties > 0
        
        return props
    
    def __repr__(self):
        return '<ContextProperties platform=%r gl_context=%r gl_sharegroup=%r>' % (self.platform, self.gl_context, self.gl_sharegroup)
    
_context_errors = {
                       CL_INVALID_PLATFORM : ('Properties is NULL and no platform could be selected or if ' 
                                              'platform value specified in properties is not a valid platform.'),
                   CL_INVALID_PROPERTY: ('Context property name in properties is not a supported ' 
                                         'property name, if the value specified for a supported property name is not valid, or if the ' 
                                         'same property name is specified more than once.'),
                   CL_INVALID_VALUE: 'pfn_notify is NULL but user_data is not NULL.',
                   CL_INVALID_DEVICE_TYPE :'device_type is not a valid value.',
                   CL_DEVICE_NOT_AVAILABLE : ('No devices that match device_type and property values' 
                                              'specified in properties are currently available.'),
                                               
                   CL_DEVICE_NOT_FOUND: ('No devices that match device_type and property values ' 
                                        'specified in properties were found.'),
                   CL_OUT_OF_RESOURCES: ('There is a failure to allocate resources required by the ' 
                                         'OpenCL implementation on the device.'),
                   CL_OUT_OF_HOST_MEMORY :('There is a failure to allocate resources required by the ' 
                                           'OpenCL implementation on the host'),
                   }
cdef class Context:
    cdef cl_context context_id
    
    def __cinit__(self):
        self.context_id = NULL
        
    def __init__(self, devices=(), device_type=None, ContextProperties properties=None):
        
        cdef cl_context_properties * props = NULL
        
        if properties is not None:
            props = properties.context_properties()
        
        cdef cl_device_type dtype
        cdef cl_int err_code
        cdef cl_uint num_devices
        cdef cl_device_id * _devices = NULL

        if device_type is not None:
            dtype = < cl_device_type > device_type
            self.context_id = clCreateContextFromType(props, dtype, NULL, NULL, & err_code)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code, _context_errors)
        else:
            if devices:
                num_devices = len(devices)
                _devices = < cl_device_id *> malloc(num_devices * sizeof(cl_device_id))
                for i in range(num_devices): 
                    _devices[i] = (< Device > devices[i]).device_id
            else:
                num_devices = 0
                _devices = NULL
                 
            self.context_id = clCreateContext(props, num_devices, _devices, NULL, NULL, & err_code)
            
            if _devices != NULL:
                free(_devices)

            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code, _context_errors)
    
    def __dealloc__(self):
        if self.context_id != NULL:
            clReleaseContext(self.context_id)
        self.context_id = NULL
        
    def __repr__(self):
        return '<opencl.Context>'
    
    def retain(self):
        clRetainContext(self.context_id)

    def release(self):
        clReleaseContext(self.context_id)
    
    property ref_count:
        def __get__(self):
            pass
        
    property devices:
        def __get__(self):
            
            cdef cl_int err_code
            cdef size_t num_devices
            cdef cl_device_id * _devices
            err_code = clGetContextInfo (self.context_id, CL_CONTEXT_DEVICES, 0, NULL, & num_devices)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
    
            _devices = < cl_device_id *> malloc(num_devices * sizeof(cl_device_id))
    
            err_code = clGetContextInfo (self.context_id, CL_CONTEXT_DEVICES, num_devices, _devices, NULL)
    
            if err_code != CL_SUCCESS:
                free(_devices)
                raise OpenCLException(err_code)
            
            devices = []
            for i in range(num_devices): 
                device = Device()
                device.device_id = _devices[i]
                devices.append(device) 
                
            free(_devices)
            
            return devices

cdef struct UserData:
    int magic
    PyObject * function
    PyObject * args
    PyObject * kwargs
     
cdef void user_func(void * data) with gil:
    cdef UserData user_data = (< UserData *> data)[0]
    
    if user_data.magic != MAGIC_NUMBER:
        raise Exception("Enqueue native kernel can not be used at this time") 

    cdef object function = < object > user_data.function
    cdef object args = < object > user_data.args
    cdef object kwargs = < object > user_data.kwargs
    
    function(*args, **kwargs)
    
    Py_DECREF(< object > user_data.function)
    Py_DECREF(< object > user_data.args)
    Py_DECREF(< object > user_data.kwargs)
    
    return
    
_enqueue_copy_buffer_errors = {
                               

    CL_INVALID_COMMAND_QUEUE: 'if command_queue is not a valid command-queue.',

    CL_INVALID_CONTEXT: ('The context associated with command_queue, src_buffer and '
    'dst_buffer are not the same or if the context associated with command_queue and events ' 
    'in event_wait_list are not the same.'),
                               
    CL_INVALID_MEM_OBJECT: 'source and dest are not valid buffer objects.',
    
    CL_INVALID_VALUE : ('source, dest, size, src_offset / cb or dst_offset / cb '
                        'require accessing elements outside the src_buffer and dst_buffer buffer objects ' 
                        'respectively. '),
    CL_INVALID_EVENT_WAIT_LIST :('event_wait_list is NULL and ' 
                                 'num_events_in_wait_list > 0, or event_wait_list is not NULL and ' 
                                 'num_events_in_wait_list is 0, or if event objects in event_wait_list are not valid events.'),
                               }

nd_range_kernel_errors = {
    CL_INVALID_PROGRAM_EXECUTABLE : ('There is no successfully built program '
                                     'executable available for device associated with command_queue.'),
    CL_INVALID_COMMAND_QUEUE : 'command_queue is not a valid command-queue.',
    CL_INVALID_KERNEL :'kernel is not a valid kernel object',
    CL_INVALID_CONTEXT: ('Context associated with command_queue and kernel are not ' 
                         'the same or if the context associated with command_queue and events in event_wait_list '
                         'are not the same.'),
    CL_INVALID_KERNEL_ARGS : 'The kernel argument values have not been specified.',
    CL_INVALID_WORK_DIMENSION : 'work_dim is not a valid value',
    CL_INVALID_GLOBAL_WORK_SIZE : ('global_work_size is NULL, or if any of the ' 
                                   'values specified in global_work_size[0], ... ' 
                                   'global_work_size[work_dim - 1] are 0 or ' 
                                   'exceed the range given by the sizeof(size_t) for the device on which the kernel ' 
                                   'execution will be enqueued.'),
    CL_INVALID_GLOBAL_OFFSET : ('The value specified in global_work_size + the ' 
                                'corresponding values in global_work_offset for any dimensions is greater than the ' 
                                'sizeof(size t) for the device on which the kernel execution will be enqueued. '),
    CL_INVALID_WORK_GROUP_SIZE :('local_work_size is specified and number of workitems specified by global_work_size is not evenly divisible by size of work-group given ' 
                                 'by local_work_size or does not match the work-group size specified for kernel'),
    CL_INVALID_WORK_GROUP_SIZE : ('local_work_size is specified and the total number ' 
                                  'of work-items in the work-group computed as local_work_size[0] * ... ' 
                                  'local_work_size[work_dim - 1] is greater than the value specified by CL_DEVICE_MAX_WORK_GROUP_SIZE'),
    CL_INVALID_WORK_GROUP_SIZE : ('local_work_size is NULL and the ' 
                                  '__attribute__((reqd_work_group_size(X, Y, Z))) qualifier is used to ' 
                                  'declare the work-group size for kernel in the program source. '),
    CL_INVALID_WORK_ITEM_SIZE :('The number of work-items specified in any of ' 
                                'local_work_size[0], ... local_work_size[work_dim - 1]    is greater than the ' 
                                'corresponding values specified by CL_DEVICE_MAX_WORK_ITEM_SIZES[0], ...CL_DEVICE_MAX_WORK_ITEM_SIZES[work_dim - 1].'),
    CL_MISALIGNED_SUB_BUFFER_OFFSET : ('A sub-buffer object is specified as the value ' 
                                       'for an argument that is a buffer object and the offset specified when the sub-buffer object ' 
                                       'is created is not aligned to CL_DEVICE_MEM_BASE_ADDR_ALIGN value for device ' 
                                       'associated with queue.'),
    CL_INVALID_IMAGE_SIZE : ('An image object is specified as an argument value and the ' 
                             'image dimensions (image width, height, specified or compute row and/or slice pitch) are ' 
                             'not supported by device associated with queue.'),
    CL_OUT_OF_RESOURCES  : 'CL_OUT_OF_RESOURCES, There is a failure to queue the execution instance of kernel ',
    CL_MEM_OBJECT_ALLOCATION_FAILURE :('There is a failure to allocate memory for ' 
                                       'data store associated with image or buffer objects specified as arguments to kernel. '),
    CL_INVALID_EVENT_WAIT_LIST: ('event_wait_list is NULL and ' 
                                 'num_events_in_wait_list > 0, or event_wait_list is not NULL and ' 
                                 'num_events_in_wait_list is 0, or if event objects in event_wait_list are not valid events. '),
    CL_OUT_OF_HOST_MEMORY : ('There is a failure to allocate resources required by the' 
                             'OpenCL implementation on the host')
}

cdef class Queue:
    
    cdef cl_command_queue queue_id
    
    def __cinit__(self, Context context, Device device, out_of_order_exec_mode=False, profiling=False):
        
        cdef cl_command_queue_properties properties = 0
        
        properties |= CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE if out_of_order_exec_mode else 0
        properties |= CL_QUEUE_PROFILING_ENABLE if profiling else 0
            
        cdef cl_int err_code = CL_SUCCESS
       
        self.queue_id = clCreateCommandQueue(context.context_id, device.device_id, properties, & err_code)
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)

    property device:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_device_id device_id
             
            err_code = clGetCommandQueueInfo (self.queue_id, CL_QUEUE_DEVICE, sizeof(cl_device_id), & device_id, NULL)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return DeviceIDAsPyDevice(device_id) 

    property context:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_context context_id
             
            err_code = clGetCommandQueueInfo (self.queue_id, CL_QUEUE_CONTEXT, sizeof(cl_context), & context_id, NULL)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return ContextAsPyContext(context_id) 
        
    def barrier(self):
        cdef cl_int err_code
        cdef cl_command_queue queue_id = self.queue_id
         
        err_code = clEnqueueBarrier(queue_id)

        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
    def flush(self):
        cdef cl_int err_code
         
        err_code = clFlush(self.queue_id)

        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)

    def finish(self):
        
        cdef cl_int err_code
        cdef cl_command_queue queue_id = self.queue_id
        
        with nogil:
            err_code = clFinish(queue_id) 

        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
    def marker(self):
        
        
        cdef Event event = Event()
        cdef cl_int err_code
         
        err_code = clEnqueueMarker(self.queue_id, & event.event_id)
         
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
        return event
        
    def copy(self, source, dest):
        pass
    
#    def enqueue_read_buffer(self, buffer, host_destination, size_t offset=0, size=None, blocking=False, events=None):
#        
#        cdef cl_int err_code
#        cdef Py_buffer view
#
#        cdef cl_bool blocking_read = 1 if blocking else 0
#        cdef void * ptr = NULL
#        cdef cl_uint num_events_in_wait_list = 0
#        cdef cl_event * event_wait_list = NULL
#        cdef Event event = Event()   
#        cdef size_t cb   
#        cdef cl_mem buffer_id = (< Buffer > buffer).buffer_id
#
#        if PyObject_GetBuffer(host_destination, & view, PyBUF_SIMPLE | PyBUF_ANY_CONTIGUOUS):
#            raise ValueError("argument 'host_buffer' must be a readable buffer object")
#        
#        if size is None:
#            cb = min(view.len, buffer.size)
#            
#        if view.len < size:
#            raise Exception("destination (host) buffer is too small")
#        elif buffer.size < size:
#            raise Exception("source (device) buffer is too small")
#        
#        ptr = view.buf
#        
#        if events:
#            num_events_in_wait_list = len(events)
#            event_wait_list = < cl_event *> malloc(num_events_in_wait_list * sizeof(cl_event))
#            
#            for i in range(num_events_in_wait_list):
#                tmp_event = < Event > events[i]
#                event_wait_list[i] = tmp_event.event_id
#            
#        err_code = clEnqueueReadBuffer (self.queue_id, buffer_id,
#                                        blocking_read, offset, cb, ptr,
#                                        num_events_in_wait_list, event_wait_list, & event.event_id)
#    
#        if event_wait_list != NULL:
#            free(event_wait_list)
#        
#        if err_code != CL_SUCCESS:
#            raise OpenCLException(err_code)
#
#        if not blocking:
#            return event
#        
#    def enqueue_map_buffer(self, buffer, blocking=False, size_t offset=0, size=None, events=None, read=True, write=True, format="B", itemsize=1):
#        
#        cdef void * host_buffer = NULL
#        cdef cl_mem _buffer
#        cdef cl_bool blocking_map = 1 if blocking else 0
#        cdef cl_map_flags map_flags = 0
#        cdef size_t cb = 0
#        cdef cl_uint num_events_in_wait_list = 0
#        cdef cl_event * event_wait_list = NULL
#        cdef Event event
#        cdef cl_int err_code
#        
#        if read:
#            map_flags |= CL_MAP_READ
#        if write:
#            map_flags |= CL_MAP_WRITE
#            
#        
#
#        _buffer = (< Buffer > buffer).buffer_id
#        
#        if size is None:
#            cb = buffer.size - offset
#        else:
#            cb = < size_t > size
#            
#            
##        cdef Py_buffer * view = < Py_buffer *> malloc(sizeof(Py_buffer)) 
##        
##        cdef char * _format = < char *> format
##        view.itemsize = itemsize
##        
##        if not view.itemsize:
##            raise Exception()
##        if (cb % view.itemsize) != 0:
##            raise Exception("size-offset must be a multiple of itemsize of format %r (%i)" % (format, view.itemsize))
#
#        if events:
#            num_events_in_wait_list = len(events)
#            event_wait_list = < cl_event *> malloc(num_events_in_wait_list * sizeof(cl_event))
#            
#            for i in range(num_events_in_wait_list):
#                tmp_event = < Event > events[i]
#                event_wait_list[i] = tmp_event.event_id
#                
#        
#        host_buffer = clEnqueueMapBuffer (self.queue_id, _buffer, blocking_map, map_flags,
#                                          offset, cb, num_events_in_wait_list, event_wait_list,
#                                          & event.event_id, & err_code)
##        print "clEnqueueMapBuffer"
#        
#        
#        if event_wait_list != NULL:
#            free(event_wait_list)
#        
#        if err_code != CL_SUCCESS:
#            raise OpenCLException(err_code)
#
#        if host_buffer == NULL:
#            raise Exception("host buffer is null")
#        
#        if write:
#            memview = < object > PyBuffer_FromReadWriteMemory(host_buffer, cb)
#        else:
#            memview = < object > PyBuffer_FromMemory(host_buffer, cb)
#            
##        view.buf = host_buffer
##        view.len = cb
##        view.readonly = 0 if write else 1
##        view.format = _format
##        view.ndim = 1
##        view.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t))
##        view.shape[0] = cb / view.itemsize 
##        view.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t))
##        view.strides[0] = 1
##        view.suboffsets = < Py_ssize_t *> malloc(sizeof(Py_ssize_t))
##        view.suboffsets[0] = 0
##         
##        view.internal = NULL 
##         
##        
#        
#        
#        if not blocking:
#            return (memview, event)
#        else:
#            return (memview, None)
#        
#    def enqueue_unmap(self, memobject, buffer, events=None,):
#
#        cdef void * mapped_ptr = NULL
#        cdef cl_mem memobj = NULL 
#        cdef cl_uint num_events_in_wait_list = 0
#        cdef cl_event * event_wait_list = NULL
#        cdef Event event = Event()
#        
#        cdef cl_int err_code
#        memobj = (< Buffer > memobject).buffer_id
#        cdef Py_ssize_t buffer_len
#        
#        PyObject_AsReadBuffer(< PyObject *> buffer, & mapped_ptr, & buffer_len)
#
#        if events:
#            num_events_in_wait_list = len(events)
#            event_wait_list = < cl_event *> malloc(num_events_in_wait_list * sizeof(cl_event))
#            
#            for i in range(num_events_in_wait_list):
#                tmp_event = < Event > events[i]
#                event_wait_list[i] = tmp_event.event_id
#                
#        err_code = clEnqueueUnmapMemObject(self.queue_id, memobj, mapped_ptr, num_events_in_wait_list,
#                                        event_wait_list, & event.event_id)
#        
#        if event_wait_list != NULL:
#            free(event_wait_list)
#        
#        if err_code != CL_SUCCESS:
#            raise OpenCLException(err_code)
#        
#        return event
    
    def enqueue_native_kernel(self, function, *args, **kwargs):
        
        cdef UserData user_data
        
        user_data.magic = MAGIC_NUMBER 
        
        user_data.function = < PyObject *> function
        
        user_data.args = < PyObject *> args
        user_data.kwargs = < PyObject *> kwargs
        
        Py_INCREF(< object > user_data.function)
        Py_INCREF(< object > user_data.args)
        Py_INCREF(< object > user_data.kwargs)
                    
        cdef cl_int err_code
        cdef Event event = Event()
        cdef cl_uint num_events_in_wait_list = 0
        cdef cl_event * event_wait_list = NULL
        cdef cl_uint  num_mem_objects = 0 
        cdef cl_mem * mem_list = NULL
        cdef void ** args_mem_loc = NULL

        cdef void * _args = < void *>& user_data
        cdef size_t cb_args = sizeof(UserData)
        
        err_code = clEnqueueNativeKernel(self.queue_id,
                                      & user_func,
                                      _args,
                                      cb_args,
                                      num_mem_objects,
                                      mem_list,
                                      args_mem_loc,
                                      num_events_in_wait_list,
                                      event_wait_list,
                                      & event.event_id) 
                            
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
    
        return event
    
    
    def enqueue_nd_range_kernel(self, kernel, cl_uint  work_dim,
                                global_work_size, global_work_offset=None, local_work_size=None, wait_on=()):
        
        cdef cl_kernel kernel_id = (< Kernel > kernel).kernel_id
        cdef Event event = Event()
        
        cdef size_t * gsize = < size_t *> malloc(sizeof(size_t) * work_dim)
        cdef size_t * goffset = NULL
        cdef size_t * lsize = NULL
        if global_work_offset:
            goffset = < size_t *> malloc(sizeof(size_t) * work_dim)
        if local_work_size:
            lsize = < size_t *> malloc(sizeof(size_t) * work_dim)
         
        for i in range(work_dim):
            gsize[i] = < size_t > global_work_size[i]
            if goffset != NULL: goffset[i] = < size_t > global_work_offset[i]
            if lsize != NULL: lsize[i] = < size_t > local_work_size[i]
            
        cdef cl_event * event_wait_list
        cdef cl_uint num_events_in_wait_list = _make_wait_list(wait_on, & event_wait_list)
        cdef cl_int err_code

        err_code = clEnqueueNDRangeKernel(self.queue_id, kernel_id,
                                          work_dim, goffset, gsize, lsize,
                                          num_events_in_wait_list, event_wait_list, & event.event_id)
        
        if gsize != NULL: free(gsize)
        if goffset != NULL: free(goffset)
        if lsize != NULL: free(lsize)

        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code, nd_range_kernel_errors)
        
        return event
    
    def enqueue_copy_buffer(self, source, dest, size_t src_offset=0, size_t dst_offset=0, size_t size=0, wait_on=()):
        
        cdef cl_int err_code
        cdef Event event = Event()
        cdef cl_event * event_wait_list
        cdef cl_uint num_events_in_wait_list = _make_wait_list(wait_on, & event_wait_list)
        
        cdef cl_mem src_buffer = (< MemoryObject > source).buffer_id
        cdef cl_mem dst_buffer = (< MemoryObject > dest).buffer_id
        
        err_code = clEnqueueCopyBuffer(self.queue_id, src_buffer, dst_buffer, src_offset, dst_offset, size,
                                       num_events_in_wait_list, event_wait_list, & event.event_id)
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code, _enqueue_copy_buffer_errors)
    
        return event

    def enqueue_read_buffer(self, source, dest, size_t src_offset=0, size_t size=0, wait_on=(), cl_bool blocking_read=0):
        
        cdef cl_int err_code
        cdef Event event = Event()
        cdef cl_event * event_wait_list
        cdef cl_uint num_events_in_wait_list = _make_wait_list(wait_on, & event_wait_list)
        
        cdef cl_mem src_buffer = (< MemoryObject > source).buffer_id
        
        cdef int flags = PyBUF_SIMPLE
        
        if not PyObject_CheckBuffer(dest):
            raise Exception("dest argument of enqueue_read_buffer is required to be a new style buffer object (got %r)" % dest)

        cdef Py_buffer dst_buffer
        
        if PyObject_GetBuffer(dest, & dst_buffer, flags) < 0:
            raise Exception("dest argument of enqueue_read_buffer is required to be a new style buffer object")
        
        if dst_buffer.len < size:
            raise Exception("dest buffer must be at least `size` bytes")
        
        if not PyBuffer_IsContiguous(& dst_buffer, 'A'):
            raise Exception("dest buffer must be contiguous")
        
        err_code = clEnqueueReadBuffer(self.queue_id, src_buffer, blocking_read, src_offset, size, dst_buffer.buf,
                                       num_events_in_wait_list, event_wait_list, & event.event_id)
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code, _enqueue_copy_buffer_errors)
    
        return event
    
    def enqueue_write_buffer(self, source, dest, size_t src_offset=0, size_t size=0, wait_on=(), cl_bool blocking_read=0):
        
        cdef cl_int err_code
        cdef Event event = Event()
        cdef cl_event * event_wait_list
        cdef cl_uint num_events_in_wait_list = _make_wait_list(wait_on, & event_wait_list)
        
        cdef cl_mem src_buffer = (< MemoryObject > source).buffer_id
        
        cdef int flags = PyBUF_SIMPLE | PyBUF_WRITABLE
        
        if not PyObject_CheckBuffer(dest):
            raise Exception("dest argument of enqueue_read_buffer is required to be a new style buffer object (got %r)" % dest)

        cdef Py_buffer dst_buffer
        
        if PyObject_GetBuffer(dest, & dst_buffer, flags) < 0:
            raise Exception("dest argument of enqueue_read_buffer is required to be a new style buffer object")
        
        if dst_buffer.len < size:
            raise Exception("dest buffer must be at least `size` bytes")
        
        if not PyBuffer_IsContiguous(& dst_buffer, 'A'):
            raise Exception("dest buffer must be contiguous")

        if dst_buffer.readonly:
            raise Exception("host buffer must have write access")
        
        err_code = clEnqueueWriteBuffer(self.queue_id, src_buffer, blocking_read, src_offset, size, dst_buffer.buf,
                                       num_events_in_wait_list, event_wait_list, & event.event_id)
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code, _enqueue_copy_buffer_errors)
    
        return event


    def enqueue_copy_buffer_rect(self, source, dest, region, src_origin=(0, 0, 0), dst_origin=(0, 0, 0),
                                 size_t src_row_pitch=0, size_t src_slice_pitch=0,
                                 size_t dst_row_pitch=0, size_t dst_slice_pitch=0, wait_on=()):
        
        cdef cl_int err_code
        cdef Event event = Event()
        cdef cl_event * event_wait_list
        cdef cl_uint num_events_in_wait_list = _make_wait_list(wait_on, & event_wait_list)
        
        cdef cl_mem src_buffer = (< MemoryObject > source).buffer_id
        cdef cl_mem dst_buffer = (< MemoryObject > dest).buffer_id
        
        cdef size_t _src_origin[3]
        _src_origin[:] = [0, 0, 0]
        cdef  size_t _dst_origin[3]
        _dst_origin[:] = [0, 0, 0]
        cdef size_t _region[3]
        _region[:] = [1, 1, 1]
        
        for i, origin in enumerate(src_origin):
            _src_origin[i] = origin

        for i, origin in enumerate(dst_origin):
            _dst_origin[i] = origin

        for i, size in enumerate(region):
            _region[i] = size
        
        err_code = clEnqueueCopyBufferRect(self.queue_id, src_buffer, dst_buffer,
                                           _src_origin, _dst_origin, _region,
                                           src_row_pitch, src_slice_pitch,
                                           dst_row_pitch, dst_slice_pitch,
                                           num_events_in_wait_list, event_wait_list, & event.event_id)
                
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code, _enqueue_copy_buffer_errors)
    
        return event

cdef cl_uint _make_wait_list(wait_on, cl_event ** event_wait_list_ptr):
    if not wait_on:
        event_wait_list_ptr[0] = NULL
        return 0
    
    cdef cl_uint num_events = len(wait_on)
    cdef Event event
    cdef cl_event * event_wait_list = < cl_event *> malloc(sizeof(cl_event) * num_events)
    
    for i, pyevent in enumerate(wait_on):
        event = < Event > pyevent
        event_wait_list[i] = event.event_id
        
    event_wait_list_ptr[0] = event_wait_list
    return num_events
    

cdef class Event:
    cdef cl_event event_id

    def wait(self):
        
        cdef cl_int err_code
        
        err_code = clWaitForEvents(1, & self.event_id)
    
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)

cdef class UserEvent(Event):

    def __cinit__(self, Context context):
        
        cdef cl_int err_code

        self.event_id = clCreateUserEvent(context.context_id, & err_code)

        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
    def complete(self):
        
        cdef cl_int err_code
        
        err_code = clSetUserEventStatus(self.event_id, CL_COMPLETE)
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
        
cdef class MemoryObject:
    cdef cl_mem buffer_id
    
    def __cinit__(self):
        self.buffer_id = NULL
        
    def __dealloc__(self):
        if self.buffer_id != NULL:
            clReleaseMemObject(self.buffer_id)
        self.buffer_id = NULL
    
    property context:
        def __get__(self):
            cdef cl_context param_value
            cdef cl_int err_code
            
            err_code = clGetMemObjectInfo(self.buffer_id, CL_MEM_CONTEXT, sizeof(size_t),
                                          < void *> & param_value, NULL)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
    
            return ContextAsPyContext(param_value)

            
    property mem_size:
        def __get__(self):
    
            cdef size_t param_value
            cdef cl_int err_code
            
            err_code = clGetMemObjectInfo(self.buffer_id, CL_MEM_SIZE, sizeof(size_t),
                                          < void *> & param_value, NULL)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
    
            return param_value

    property _refcount:
        def __get__(self):
            cdef cl_uint param_value
            cdef cl_int err_code
            clGetMemObjectInfo (self.buffer_id, CL_MEM_REFERENCE_COUNT, sizeof(cl_uint),
                                < void *>& param_value, NULL)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)

            return param_value

    property _mapcount:
        def __get__(self):
            
            cdef cl_uint param_value
            cdef cl_int err_code
            clGetMemObjectInfo (self.buffer_id, CL_MEM_MAP_COUNT, sizeof(cl_uint),
                                < void *>& param_value, NULL)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)

            return param_value
    
    property base:
        def __get__(self):
            cdef cl_mem param_value
            cdef cl_int err_code
            clGetMemObjectInfo (self.buffer_id, CL_MEM_ASSOCIATED_MEMOBJECT, sizeof(cl_mem),
                                < void *>& param_value, NULL)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            if param_value == NULL:
                return None
            else:
                return MemObjectAs_pyMemoryObject(param_value)
    
    
cdef class DeviceMemoryView(MemoryObject):
    
    cdef char * _format
    cdef public int readonly
    cdef public int ndim
    cdef Py_ssize_t * _shape
    cdef Py_ssize_t * _strides
    cdef Py_ssize_t * _suboffsets
    cdef public Py_ssize_t itemsize
    cdef object __weakref__
    
    def __cinit__(self):
        self._format = NULL
        self.readonly = 1
        self.ndim = 0
        self._shape = NULL
        self._strides = NULL
        self._suboffsets = NULL
        self.itemsize = 0
        
    def __init__(self, Context context, size_t size, cl_mem_flags flags=CL_MEM_READ_WRITE):
        
        self.buffer_id = NULL 
        cdef void * host_ptr = NULL
        cdef cl_int err_code
        self.buffer_id = clCreateBuffer(context.context_id, flags, size, host_ptr, & err_code)

        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
    
    property format:
        def __get__(self):
            if self._format != NULL:
                return str(self._format)
            else:
                return "B"
        
    property shape:
        def __get__(self):
            shape = []
            for i in range(self.ndim):
                shape.append(self._shape[i])
            return tuple(shape)

    property suboffsets:
        def __get__(self):
            
            if self._suboffsets == NULL:
                return None
            
            suboffsets = []
            for i in range(self.ndim):
                suboffsets.append(self._suboffsets[i])
            return tuple(suboffsets)

    property strides:
        def __get__(self):
            strides = []
            for i in range(self.ndim):
                strides.append(self._strides[i])
            return tuple(strides)
        
    def map(self, queue, blocking=True, readonly=False, size_t offset=0, size_t size=0):
        
        cdef cl_map_flags flags = CL_MAP_READ
        
        if not readonly: 
            flags |= CL_MAP_WRITE
        
        cdef cl_bool blocking_map = 1 if blocking else 0
        if size == 0:
            size = len(self)
            
        return MemoryViewMap(< Queue > queue, self, blocking_map, flags, offset, size)

    @classmethod
    def from_host(cls, Context ctx, host):
        
        cdef Py_buffer view
        cdef DeviceMemoryView buffer = DeviceMemoryView.__new__(DeviceMemoryView)
        
        cdef int py_flags = PyBUF_SIMPLE | PyBUF_STRIDES | PyBUF_ND | PyBUF_FORMAT
        
        cdef cl_mem_flags mem_flags = CL_MEM_COPY_HOST_PTR | CL_MEM_READ_WRITE
        cdef cl_int err_code
         
        if not PyObject_CheckBuffer(host):
            raise Exception("argument host must support the buffer protocal (got %r)" % host)
        
        if PyObject_GetBuffer(host, & view, py_flags) < 0:
            raise Exception("argument host must support the buffer protocal (got %r)" % host)
            
        if PyBuffer_IsContiguous(& view, 'C'):
            buffer.buffer_id = clCreateBuffer(ctx.context_id, mem_flags, view.len, view.buf, & err_code)
            PyBuffer_Release(& view)
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            buffer._format = view.format
            buffer.readonly = 1
            buffer.itemsize = view.itemsize
            buffer.ndim = view.ndim
            
            buffer._shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * view.ndim)
            buffer._strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * view.ndim)
            buffer._suboffsets = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * view.ndim)
            
            for i in range(view.ndim):
                buffer._shape[i] = view.shape[i]
                buffer._strides[i] = view.strides[i]
                buffer._suboffsets[i] = 0

        else:
            raise NotImplementedError("data must be contiguous")
        
        return buffer
        
    @classmethod
    def from_gl(cls, Context ctx, vbo):
        
        cdef cl_context context = ctx.context_id
        cdef cl_mem_flags flags = CL_MEM_READ_WRITE
        cdef unsigned int bufobj = vbo
        cdef cl_int err_code
        cdef cl_mem memobj = NULL
        
        memobj = clCreateFromGLBuffer(context, flags, bufobj, & err_code)
    
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
        cdef MemoryObject cview = < MemoryObject > MemoryObject.__new__(MemoryObject)
        
        return None

    
    def __getitem__(self, args):
        
        if not isinstance(args, tuple):
            args = (args,)
            
        if len(args) != self.ndim:
            raise IndexError("too many indices expected %i (got %i)" % (self.ndim, len(args)))
        
        ndim = self.ndim
        shape = list(self.shape)
        strides = list(self.strides)
        suboffsets = list(self.suboffsets)
        i = 0 
        for arg in args:
            if isinstance(arg, slice):
                start, stop, step = arg.indices(shape[i])
                shape[i] = (stop - start) // step
                modd = (stop - start) % step
                if modd != 0: shape[i] += 1
                
                if suboffsets[i] > 0:
                    suboffsets[i] += start * strides[i]
                else:
                    suboffsets[i] = start * strides[i]
                    
                strides[i] = strides[i] * step
                i += 1
            else:
                raise IndexError()
        
        cdef DeviceMemoryView buffer = DeviceMemoryView.__new__(DeviceMemoryView)
        
        clRetainMemObject(self.buffer_id) 
        buffer.buffer_id = self.buffer_id
        
        buffer._format = self._format
        buffer.readonly = self.readonly
        buffer.itemsize = self.itemsize
        buffer.ndim = ndim
        
        buffer._shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
        buffer._strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
        buffer._suboffsets = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
        
        for i in range(ndim):
            buffer._shape[i] = shape[i]
            buffer._strides[i] = strides[i]
            buffer._suboffsets[i] = suboffsets[i]
        
        return buffer
    
    property size:
        def __get__(self):
            shape = self.shape
            size = 1
            for i in range(self.ndim):
                size *= shape[i]
            return size

    property nbytes:
        def __get__(self):
            return self.size * self.itemsize

    property offset:
        def __get__(self):
            cdef size_t offset = 0
            
            for i in range(self.ndim):
                offset += self._suboffsets[i]
                
            return offset

        
    def __len__(self):
        return self.size 
            
    property is_contiguous:
        def __get__(self):
            
            strides = [self.itemsize]
            for i in range(self.ndim - 1):
                stride = strides[i]
                size = self.shape[-i - 1]
                strides.append(stride * size)
                
            return self.strides == tuple(strides[::-1])
        
    def copy(self, queue):
        
        cdef size_t src_row_pitch  
        cdef size_t src_slice_pitch 
        cdef size_t dst_row_pitch
        cdef size_t dst_slice_pitch
        dest = empty(self.context, self.shape, ctype=self.format)
        
        if self.is_contiguous:
            queue.enqueue_copy_buffer(self, dest, self.offset, dst_offset=0, size=self.nbytes, wait_on=())
            
        elif any(stride < 0 for stride in self.strides):
            raise NotImplementedError("stride < 0")
        
        elif self.ndim == 1:
            
            src_row_pitch = self._strides[0]
            src_slice_pitch = 0 
            dst_row_pitch = 0
            dst_slice_pitch = 0
            
            region = (dest.itemsize, dest.size, 1)
            src_origin = (self.offset, 0, 0)
            dst_origin = (0, 0, 0)
            
            queue.enqueue_copy_buffer_rect(self, dest, region, src_origin, dst_origin,
                                           src_row_pitch, src_slice_pitch,
                                           dst_row_pitch, dst_slice_pitch, wait_on=())
        elif self.ndim == 2:
            
            shape2 = self.itemsize
            shape1 = self._shape[1]
            shape0 = self._shape[0]
            
            src_row_pitch = self._strides[1]
            src_slice_pitch = self._strides[0] 

            region = shape2, shape1, shape0
            src_origin = (self.offset, 0, 0)
            dst_origin = (0, 0, 0)
            
            queue.enqueue_copy_buffer_rect(self, dest, region, src_origin, dst_origin,
                                           src_row_pitch, src_slice_pitch,
                                           dst_row_pitch, dst_slice_pitch, wait_on=())
        else:
            raise Exception()
        
        return dest
    
    def read(self, queue, out, wait_on=(), blocking=False):
        queue.enqueue_read_buffer(self, out, self.offset, self.nbytes, wait_on, blocking_read=blocking)

    def write(self, queue, buf, wait_on=(), blocking=False):
        queue.enqueue_write_buffer(self, buf, self.offset, self.nbytes, wait_on, blocking_read=blocking)
        
#        view.len = self.cb
#        
#        cdef DeviceMemoryView dview = < DeviceMemoryView > self.dview()
#        cdef cl_mem memobj = dview.buffer_id
#        
#        view.readonly = 0 if (self.map_flags & CL_MAP_WRITE) else 1
#        view.format = dview._format
#        view.ndim = dview.ndim
#        view.shape = dview._shape
#        view.itemsize = dview.itemsize
#        view.internal = NULL
#        view.strides = dview._strides
#        view.suboffsets = NULL
#        
#        cdef size_t offset = dview.offset 
#        
#        view.buf = self.bytes + offset
        
    def __releasebuffer__(self, Py_buffer * view):
        pass


def empty_gl(Context ctx, shape, ctype='B'):
    
    cdef cl_mem_flags flags = CL_MEM_READ_WRITE
    
    cdef char * format
    cdef cl_int err_code
    
    if isinstance(ctype, str):
        format = ctype
    else:
        format = ctype._type_

    cdef size_t itemsize = struct.calcsize(format)
    cdef size_t size = itemsize
    for i in shape:
        size *= i
       
    cdef GLuint vbo 
    glGenBuffers(1, & vbo)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    
    cdef GLsizeiptr nbytes = itemsize
    for i in shape:
        nbytes *= i
                
    glBufferData(GL_ARRAY_BUFFER, nbytes, NULL, GL_STATIC_DRAW)
    
    if glGetError() != GL_NO_ERROR:
        raise Exception("OpenGL error")
    
    cdef cl_mem buffer_id = clCreateFromGLBuffer(ctx.context_id, flags, vbo, & err_code)
    
    
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    
    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)

    cdef DeviceMemoryView buffer = DeviceMemoryView.__new__(DeviceMemoryView)
    buffer.buffer_id = buffer_id
    
    buffer._format = format
    buffer.readonly = 0
    buffer.itemsize = itemsize
    buffer.ndim = len(shape)
    
    buffer._shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer._strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer._suboffsets = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    
    strides = [buffer.itemsize]
    for i in range(buffer.ndim):
        buffer._shape[i] = shape[i]
        buffer._suboffsets[i] = 0
    
    PyBuffer_FillContiguousStrides(buffer.ndim, buffer._shape, buffer._strides, buffer.itemsize, 'C')
    
    return buffer

def empty(Context ctx, shape, ctype='B'):
    
    cdef cl_mem_flags flags = CL_MEM_READ_WRITE
    
    cdef char * format
    cdef cl_int err_code
    
    if isinstance(ctype, str):
        format = ctype
    else:
        format = ctype._type_

    cdef size_t itemsize = struct.calcsize(format)
    cdef size_t size = itemsize
    for i in shape:
        size *= i
        
    cdef cl_mem buffer_id = clCreateBuffer(ctx.context_id, flags, size, NULL, & err_code)

    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)

    cdef DeviceMemoryView buffer = DeviceMemoryView.__new__(DeviceMemoryView)
    buffer.buffer_id = buffer_id
    
    buffer._format = format
    buffer.readonly = 0
    buffer.itemsize = itemsize
    buffer.ndim = len(shape)
    
    buffer._shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer._strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer._suboffsets = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    
    strides = [buffer.itemsize]
    for i in range(buffer.ndim):
        buffer._shape[i] = shape[i]
        buffer._suboffsets[i] = 0
    
    PyBuffer_FillContiguousStrides(buffer.ndim, buffer._shape, buffer._strides, buffer.itemsize, 'C')
    
    return buffer
    
cdef class MemoryViewMap:
    
    cdef cl_command_queue command_queue
#    cdef DeviceMemoryView dview
    cdef public object dview
    
    cdef cl_bool blocking_map
    cdef cl_map_flags map_flags
    cdef size_t offset
    cdef size_t cb
    cdef void * bytes 
        
    def __init__(self, Queue  queue, dview, cl_bool blocking_map, cl_map_flags map_flags, size_t offset, size_t cb):
        
        self.dview = weakref.ref(dview)
        
        self.command_queue = queue.queue_id
        self.blocking_map = blocking_map
        self.map_flags = map_flags
        self.offset = offset
        self.cb = cb
    
    def __enter__(self):
        cdef void * bytes 
        cdef cl_uint num_events_in_wait_list = 0
        cdef cl_event * event_wait_list = NULL
        
        cdef cl_int err_code
        
        cdef cl_mem memobj = (< DeviceMemoryView > self.dview()).buffer_id
        bytes = clEnqueueMapBuffer(self.command_queue, memobj,
                                   self.blocking_map, self.map_flags, 0, len(self.dview()),
                                   num_events_in_wait_list, event_wait_list, NULL,
                                   & err_code)
         
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
        self.bytes = bytes
        
        return memoryview(self)

    def __exit__(self, *args):

        cdef cl_int err_code 
        
        cdef cl_mem memobj = (< DeviceMemoryView > self.dview()).buffer_id
        
        err_code = clEnqueueUnmapMemObject(self.command_queue, memobj, self.bytes, 0, NULL, NULL)
        clEnqueueBarrier(self.command_queue)
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
    def __getbuffer__(self, Py_buffer * view, int flags):
        view.len = self.cb
        
        cdef DeviceMemoryView dview = < DeviceMemoryView > self.dview()
        cdef cl_mem memobj = dview.buffer_id
        
        view.readonly = 0 if (self.map_flags & CL_MAP_WRITE) else 1
        view.format = dview._format
        view.ndim = dview.ndim
        view.shape = dview._shape
        view.itemsize = dview.itemsize
        view.internal = NULL
        view.strides = dview._strides
        view.suboffsets = NULL
        
        cdef size_t offset = dview.offset 
        
        view.buf = self.bytes + offset
        
    def __releasebuffer__(self, Py_buffer * view):
        pass
    
cdef class Image(MemoryObject):
    pass

clCreateKernel_errors = {
                         
                         
                         }
cdef class Program:
    cdef cl_program program_id
    
    def __cinit__(self):
        self.program_id = NULL
    
    def __dealloc__(self):
        if self.program_id != NULL:
            clReleaseProgram(self.program_id)
        self.program_id = NULL
        
    def __init__(self, Context context, source=None):
        
        cdef char * strings
        cdef cl_int err_code
        if source is not None:
            
            strings = source
            self.program_id = clCreateProgramWithSource(context.context_id, 1, & strings, NULL, & err_code)
            
    def build(self, devices=None, options=''):
        
        cdef cl_int err_code
        cdef char * _options = options
        cdef cl_uint num_devices = 0
        cdef cl_device_id * device_list = NULL
        
        err_code = clBuildProgram(self.program_id, num_devices, device_list, _options, NULL, NULL)
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)

        return self
    
    property num_devices:
        def __get__(self):
            
            cdef cl_int err_code
            cdef cl_uint value
            err_code = clGetProgramInfo(self.program_id, CL_PROGRAM_NUM_DEVICES, sizeof(value), & value, NULL)

            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return value
        

    property logs:
        def __get__(self):
            
            logs = []
            cdef size_t log_len
            cdef char * logstr
            cdef cl_int err_code
            cdef cl_device_id device_id
            
            for device in self.devices:
                
                device_id = (< Device > device).device_id

                err_code = clGetProgramBuildInfo (self.program_id, device_id, CL_PROGRAM_BUILD_LOG, 0, NULL, & log_len)
                
                if err_code != CL_SUCCESS: raise OpenCLException(err_code)
                
                if log_len == 0:
                    logs.append('')
                    continue
                
                logstr = < char *> malloc(log_len + 1)
                err_code = clGetProgramBuildInfo (self.program_id, device_id, CL_PROGRAM_BUILD_LOG, log_len, logstr, NULL)
                 
                if err_code != CL_SUCCESS: 
                    free(logstr)
                    raise OpenCLException(err_code)
                
                logstr[log_len] = 0
                logs.append(logstr)
                
            return logs
                
        
    property context:
        def __get__(self):
            
            cdef cl_int err_code
            cdef Context context = Context()
            
            err_code = clGetProgramInfo (self.program_id, CL_PROGRAM_CONTEXT, sizeof(cl_context), & context.context_id, NULL)
              
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return context
        
    def kernel(self, name):
        
        cdef cl_int err_code
        cdef cl_kernel kernel_id
        cdef char * kernel_name = name
        
        kernel_id = clCreateKernel(self.program_id, kernel_name, & err_code)
    
        if err_code != CL_SUCCESS:
            if err_code == CL_INVALID_KERNEL_NAME:
                raise KeyError('kernel %s not found in program' % name)
            raise OpenCLException(err_code, clCreateKernel_errors)
        
        return KernelAsPyKernel(kernel_id)

    property devices:
        def __get__(self):
            
            cdef cl_int err_code
            cdef cl_device_id * device_list
                        
            cdef cl_uint num_devices = self.num_devices
            
            device_list = < cl_device_id *> malloc(sizeof(cl_device_id) * num_devices)
            err_code = clGetProgramInfo (self.program_id, CL_PROGRAM_DEVICES, sizeof(cl_device_id) * num_devices, device_list, NULL)
            
            if err_code != CL_SUCCESS:
                free(device_list)
                raise OpenCLException(err_code)
            
            
            devices = []
            
            for i in range(num_devices):
                devices.append(DeviceIDAsPyDevice(device_list[i]))
                
            free(device_list)
            
            return devices
        
class global_memory(object):
    def __init__(self, ctype=None, shape=None):
        self.shape = shape
        
        if ctype is None:
            self.format = ctype
            self.ctype = ctype
            
        elif isinstance(ctype, str):
            self.format = ctype
            self.ctype = ctype_from_format(ctype)
            
        else:
            self.ctype = ctype
            self.format = type_format(ctype)
    
    def __call__(self, memobj):
        if not isinstance(memobj, MemoryObject):
            raise TypeError("arguemnt must be an instance of MemoryObject")
        cdef cl_mem buffer = (< MemoryObject > memobj).buffer_id
        return ctypes.c_voidp(< size_t > buffer)
    
    def ctype_string(self):
        return '__global %s' % (cdefn(refrence(self.format)))
    
    def derefrence(self):
        return self.ctype
    
set_kerne_arg_errors = {
    CL_INVALID_KERNEL : 'kernel is not a valid kernel object.',
    CL_INVALID_ARG_INDEX :'arg_index is not a valid argument index.',
    CL_INVALID_ARG_VALUE : 'arg_value specified is not a valid value.',
    CL_INVALID_MEM_OBJECT : 'The specified arg_value is not a valid memory object.',
    CL_INVALID_SAMPLER : 'The specified arg_value is not a valid sampler object.',
    CL_INVALID_ARG_SIZE :('arg_size does not match the size of the data type for an ' 
                          'argument that is not a memory object or if the argument is a memory object and arg_size')
}

cdef class Kernel:
    cdef cl_kernel kernel_id
    cdef object _argtypes 
    cdef object _argnames 
    cdef public object global_work_size
    cdef public object global_work_offset
    cdef public object local_work_size
    
    def __cinit__(self):
        self.kernel_id = NULL

    def __dealloc__(self):
        
        if self.kernel_id != NULL:
            clReleaseKernel(self.kernel_id)
            
        self.kernel_id = NULL
        
    def __init__(self):
        self._argtypes = None
        self._argnames = None
        self.global_work_size = None
        self.global_work_offset = None
        self.local_work_size = None
        
    property argtypes:
        def __get__(self):
            return self._argtypes
        
        def __set__(self, value):
            self._argtypes = tuple(value)
            if len(self._argtypes) != self.nargs:
                raise TypeError("argtypes must have %i values (got %i)" % (self.nargs, len(self.argtypes)))
            
    property nargs:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_uint nargs

            err_code = clGetKernelInfo(self.kernel_id, CL_KERNEL_NUM_ARGS, sizeof(cl_uint), & nargs, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            
            return nargs

    property name:
        def __get__(self):
            cdef cl_int err_code
            cdef size_t nbytes
            cdef char * name = NULL
            
            err_code = clGetKernelInfo(self.kernel_id, CL_KERNEL_FUNCTION_NAME, 0, NULL, & nbytes)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            
            name = < char *> malloc(nbytes + 1)
            
            err_code = clGetKernelInfo(self.kernel_id, CL_KERNEL_FUNCTION_NAME, nbytes, name, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            
            name[nbytes] = 0
            cdef str pyname = name
            free(name)
            
            return pyname
        
        
    def __repr__(self):
        return '<Kernel %s nargs=%r>' % (self.name, self.nargs)
    
    def set_args(self, *args):
        if self._argtypes is None:
            raise TypeError("argtypes must be set before calling ")
        
        if len(args) != len(self._argtypes):
            raise TypeError("kernel requires %i arguments (got %i)" % (self.nargs, len(args)))
        
        cdef cl_int err_code
        cdef size_t arg_size
        cdef size_t tmp
        cdef void * arg_value
        
        for arg_index, (argtype, arg) in enumerate(zip(self._argtypes, args)):
            carg = argtype(arg)
            if isinstance(argtype, global_memory):
                arg_size = sizeof(cl_mem)
                arg_value = < void *> & (< MemoryObject > arg).buffer_id
            else:
                arg_size = ctypes.sizeof(carg)
                tmp = < size_t > ctypes.addressof(carg)
                arg_value = < void *> tmp
            
            err_code = clSetKernelArg(self.kernel_id, arg_index, arg_size, arg_value)
            if err_code != CL_SUCCESS:
                print arg_index, arg_size, arg 
                raise OpenCLException(err_code, set_kerne_arg_errors)
         
    def __call__(self, queue, *args, global_work_size=None, global_work_offset=None, local_work_size=None, wait_on=()):
        self.set_args(*args)
        
        if global_work_size is None:
            if isfunction(self.global_work_size):
                global_work_size = self.global_work_size(*args)
            elif self.global_work_size is None:
                raise TypeError("missing required keyword arguement 'global_work_size'")
            else:
                global_work_size = self.global_work_size

        if global_work_offset is None:
            if isfunction(self.global_work_offset):
                global_work_offset = self.global_work_offset(*args)
            else:
                global_work_offset = self.global_work_offset

        if local_work_size is None:
            if isfunction(self.local_work_size):
                local_work_size = self.local_work_size(*args)
            else:
                local_work_size = self.local_work_size
        
        queue.enqueue_nd_range_kernel(self, len(global_work_size), global_work_size, global_work_offset, local_work_size, wait_on)
    

## API FUNCTIONS #### #### #### #### #### #### #### #### #### #### ####
## ############# #### #### #### #### #### #### #### #### #### #### ####
#===============================================================================
# 
#===============================================================================

cdef api cl_platform_id clPlatformFromPyPlatform(object py_platform):
    cdef Platform platform = < Platform > py_platform
    return platform.platform_id

cdef api object clPlatformAs_PyPlatform(cl_platform_id platform_id):
    cdef Platform platform = < Platform > Platform.__new__(Platform)
    platform.platform_id = platform_id
    return platform

cdef api cl_context ContextFromPyContext(object pycontext):
    cdef Context context = < Context > pycontext
    return context.context_id

cdef api object ContextAsPyContext(cl_context context):
    ctx = < Context > Context.__new__(Context)
    clRetainContext(context)
    ctx.context_id = context
    return ctx
#===============================================================================
# 
#===============================================================================

cdef api cl_device_id DeviceIDFromPyDevice(object py_device):
    cdef Device device = < Device > py_device
    return device.device_id

cdef api object DeviceIDAsPyDevice(cl_device_id device_id):
    cdef Device device = < Device > Device.__new__(Device)
    device.device_id = device_id
    return device

#===============================================================================
# 
#===============================================================================
cdef api cl_kernel KernelFromPyKernel(object py_kernel):
    cdef Kernel kernel = < Kernel > py_kernel
    return kernel.kernel_id

cdef api object KernelAsPyKernel(cl_kernel kernel_id):
    cdef Kernel kernel = < Kernel > Kernel.__new__(Kernel)
    kernel.kernel_id = kernel_id
    clRetainKernel(kernel_id)
    return kernel


#===============================================================================
# 
#===============================================================================
cdef api cl_kernel ViewFromMemObject(object py_kernel):
    cdef Kernel kernel = < Kernel > py_kernel
    return kernel.kernel_id

cdef api object MemObjectAs_pyMemoryObject(cl_mem buffer_id):
    cdef MemoryObject cview = < MemoryObject > MemoryObject.__new__(MemoryObject)
    clRetainMemObject(buffer_id)
    cview.buffer_id = buffer_id
    return cview

## ############# #### #### #### #### #### #### #### #### #### #### ####

