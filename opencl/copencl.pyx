'''

'''
import weakref
import struct
import ctypes
from opencl.type_formats import refrence, ctype_from_format, type_format, cdefn
from opencl.errors import OpenCLException

from libc.stdlib cimport malloc, free 
from libc.stdio cimport printf
from _cl cimport * 
from cpython cimport PyObject, Py_DECREF, Py_INCREF, PyBuffer_IsContiguous, PyBuffer_FillContiguousStrides
from cpython cimport Py_buffer, PyBUF_SIMPLE, PyBUF_STRIDES, PyBUF_ND, PyBUF_FORMAT, PyBUF_INDIRECT, PyBUF_WRITABLE

from opencl.kernel cimport KernelFromPyKernel, KernelAsPyKernel
from opencl.context cimport CyContext_GetID, CyContext_Create, CyContext_Check

cdef extern from "Python.h":
    void PyEval_InitThreads()

MAGIC_NUMBER = 0xabc123

PyEval_InitThreads()


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
        return '<opencl.Device name=%r type=%r>' % (self.name, self.type,)
    
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
            
    property type:
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

    property queue_properties:
        def __get__(self):
            cdef size_t size
            cdef cl_int err_code
            cdef cl_command_queue_properties result
            
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_QUEUE_PROPERTIES, sizeof(cl_command_queue_properties), & result, NULL)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return result 
        
    property has_queue_out_of_order_exec_mode:
        def __get__(self):
            return bool((<cl_command_queue_properties> self.queue_properties) & CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE)

    property has_queue_profiling:
        def __get__(self):
            return bool((<cl_command_queue_properties> self.queue_properties) & CL_QUEUE_PROFILING_ENABLE)
        
    property has_native_kernel:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_device_exec_capabilities result
            
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_EXECUTION_CAPABILITIES, sizeof(cl_device_exec_capabilities), & result, NULL)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return True if result & CL_EXEC_NATIVE_KERNEL else False 

    property vendor_id:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_uint value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_VENDOR_ID, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value
        
    property max_compute_units:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_uint value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_MAX_COMPUTE_UNITS, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value

    property max_work_item_dimensions:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_uint value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_MAX_WORK_ITEM_DIMENSIONS, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value

    property max_clock_frequency:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_uint value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_MAX_CLOCK_FREQUENCY, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value

    property address_bits:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_uint value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_ADDRESS_BITS, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value
        
    property max_read_image_args:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_uint value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_MAX_READ_IMAGE_ARGS, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value

    property max_write_image_args:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_uint value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_MAX_WRITE_IMAGE_ARGS, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value

    property global_mem_size:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_ulong value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_GLOBAL_MEM_SIZE, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value
    property max_mem_alloc_size:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_ulong value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_MAX_MEM_ALLOC_SIZE, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value

    property max_const_buffer_size:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_ulong value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_MAX_CONSTANT_BUFFER_SIZE, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value

    property has_local_mem:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_device_local_mem_type value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_LOCAL_MEM_TYPE, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value == CL_LOCAL

    property local_mem_size:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_ulong value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_LOCAL_MEM_SIZE, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value

    property host_unified_memory:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_bool value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_HOST_UNIFIED_MEMORY, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return bool(value)

    property available:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_bool value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_AVAILABLE, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return bool(value)

    property compiler_available:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_bool value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_COMPILER_AVAILABLE, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return bool(value)

    property max_work_item_sizes:
        def __get__(self):
            cdef cl_int err_code
            cdef size_t dims = self.max_work_item_dimensions
            cdef size_t nbytes = sizeof(size_t) * dims
            cdef size_t * value = < size_t *> malloc(nbytes)
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_MAX_WORK_ITEM_SIZES, nbytes, < void *> value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            
            return [value[i] for i in range(dims)]

    property max_work_group_size:
        def __get__(self):
            cdef cl_int err_code
            cdef size_t value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_MAX_WORK_GROUP_SIZE, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value

    property profiling_timer_resolution:
        def __get__(self):
            cdef cl_int err_code
            cdef size_t value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_PROFILING_TIMER_RESOLUTION, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value

    property max_parameter_size:
        def __get__(self):
            cdef cl_int err_code
            cdef size_t value = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_MAX_PARAMETER_SIZE, sizeof(value), < void *>& value, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return value

    property max_image2d_shape:
        def __get__(self):
            cdef cl_int err_code
            cdef size_t w = 0
            cdef size_t h = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_IMAGE2D_MAX_WIDTH, sizeof(w), < void *>& w, NULL)
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_IMAGE2D_MAX_HEIGHT, sizeof(h), < void *>& h, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return [w, h]

    property max_image3d_shape:
        def __get__(self):
            cdef cl_int err_code
            cdef size_t w = 0
            cdef size_t h = 0
            cdef size_t d = 0
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_IMAGE3D_MAX_WIDTH, sizeof(w), < void *>& w, NULL)
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_IMAGE3D_MAX_HEIGHT, sizeof(h), < void *>& h, NULL)
            err_code = clGetDeviceInfo(self.device_id, CL_DEVICE_IMAGE3D_MAX_DEPTH, sizeof(d), < void *>& d, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            return [w, h, d]

    cdef get_info(self, cl_device_info info_type):
        cdef size_t size
        cdef cl_int err_code
        err_code = clGetDeviceInfo(self.device_id, info_type, 0, NULL, & size)
        if err_code != CL_SUCCESS: raise OpenCLException(err_code)
        
        cdef char * result = < char *> malloc(size * sizeof(char *))
        
        err_code = clGetDeviceInfo(self.device_id, info_type, size, result, NULL)
        
        if err_code != CL_SUCCESS:
            free(result)
            raise OpenCLException(err_code)
        
        cdef bytes a_python_byte_string = result
        free(result)
        return a_python_byte_string

    property driver_version:
        def __get__(self):
            return self.get_info(CL_DRIVER_VERSION)

    property version:
        def __get__(self):
            return self.get_info(CL_DEVICE_PROFILE)
        
    property profile:
        def __get__(self):
            return self.get_info(CL_DEVICE_VERSION)
        
    property extensions:
        def __get__(self):
            return self.get_info(CL_DEVICE_EXTENSIONS).split()


cdef void pfn_event_notify(cl_event event, cl_int event_command_exec_status, void * data) with gil:
    
    cdef object user_data = (< object > data)
    
    pyevent = cl_eventAs_PyEvent(event)
    
    try:
        user_data(pyevent, event_command_exec_status)
    except:
        Py_DECREF(< object > user_data)
        raise
    else:
        Py_DECREF(< object > user_data)
    

cdef class Event:

    QUEUED = CL_QUEUED
    SUBMITTED = CL_SUBMITTED
    RUNNING = CL_RUNNING
    COMPLETE = CL_COMPLETE
    
    STATUS_DICT = { CL_QUEUED: 'queued', CL_SUBMITTED:'submitted', CL_RUNNING: 'running', CL_COMPLETE:'complete'}
    
    cdef cl_event event_id
    
    def __cinit__(self):
        self.event_id = NULL

    def __dealloc__(self):
        if self.event_id != NULL:
            clReleaseEvent(self.event_id)
        self.event_id = NULL
        
    def __repr__(self):
        status = self.status
        return '<%s status=%r:%r>' % (self.__class__.__name__, status, self.STATUS_DICT[status])
    
    def wait(self):
        
        cdef cl_int err_code
        
        with nogil:
            err_code = clWaitForEvents(1, & self.event_id)
    
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
    property status:
        def __get__(self):
            cdef cl_int err_code
            cdef cl_int status

            err_code = clGetEventInfo(self.event_id, CL_EVENT_COMMAND_EXECUTION_STATUS, sizeof(cl_int), & status, NULL)

            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return status
        
    def add_callback(self, callback):
        
        cdef cl_int err_code

        Py_INCREF(callback)
        err_code = clSetEventCallback(self.event_id, CL_COMPLETE, < void *> & pfn_event_notify, < void *> callback) 
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
        
cdef class UserEvent(Event):

    def __cinit__(self, context):
        
        cdef cl_int err_code

        cdef cl_context ctx = CyContext_GetID(context)
        self.event_id = clCreateUserEvent(ctx, & err_code)

        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
    def complete(self):
        
        cdef cl_int err_code
        
        err_code = clSetUserEventStatus(self.event_id, CL_COMPLETE)
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        

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
        
    def __init__(self, context, source=None, binaries=None, devices=None):
        
        cdef char * strings
        cdef cl_int err_code
        
        if not CyContext_Check(context):
            raise TypeError("argument 'context' must be a valid opencl.Context object")
        cdef cl_context ctx = CyContext_GetID(context)
        
        cdef cl_uint num_devices
        cdef cl_device_id * device_list
        cdef size_t * lengths 
        cdef unsigned char ** bins
        cdef cl_int * binary_status
        
        
        if source is not None:
            
            strings = source
            self.program_id = clCreateProgramWithSource(ctx, 1, & strings, NULL, & err_code)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)

        elif binaries is not None:
            
            num_devices = len(binaries)
            
            device_list = < cl_device_id *> malloc(sizeof(cl_device_id) * num_devices)
            lengths = < size_t *> malloc(sizeof(size_t) * num_devices)
            bins = <unsigned char **> malloc(sizeof(unsigned char *) * num_devices)
            binary_status = <cl_int *> malloc(sizeof(cl_int) * num_devices)
            
            try:
                for i,(device, binary) in enumerate(binaries.items()):
                    
                    if not CyDevice_Check(device):
                        raise TypeError("argument binaries must be a dict of device:binary pairs")
                    
                    device_list[i] = CyDevice_GetID(device)
                    lengths[i] = len(binary)
                    bins[i] = binary
                    
                self.program_id = clCreateProgramWithBinary(ctx, num_devices, device_list, lengths, bins, binary_status, & err_code)
    
                if err_code != CL_SUCCESS:
                    raise OpenCLException(err_code)
                
                for i in range(num_devices):
                    status = binary_status[i]
                    if status != CL_SUCCESS:
                        raise OpenCLException(status)
            except:
                free(device_list)
                free(lengths)
                free(bins)
                free(binary_status)
                raise
            free(device_list)
            free(lengths)
            free(bins)
            free(binary_status)
            
            
            
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
            cdef cl_uint value = 0 
            err_code = clGetProgramInfo(self.program_id, CL_PROGRAM_NUM_DEVICES, sizeof(value), & value, NULL)

            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return value
        
    property _reference_count:
        def __get__(self):
            
            cdef cl_int err_code
            cdef cl_uint value = 0 
            err_code = clGetProgramInfo(self.program_id, CL_PROGRAM_REFERENCE_COUNT, sizeof(value), & value, NULL)

            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return value
        

    property source:
        def __get__(self):
            
            cdef cl_int err_code
            cdef char * src = NULL
            cdef size_t src_len = 0 
            err_code = clGetProgramInfo(self.program_id, CL_PROGRAM_SOURCE, 0, NULL, & src_len)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            
            if src_len <= 1:
                return None
            
            src = < char *> malloc(src_len + 1)
            
            err_code = clGetProgramInfo(self.program_id, CL_PROGRAM_SOURCE, src_len, src, NULL)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            
            src[src_len] = 0
            return src

    property binary_sizes:
        def __get__(self):
            
            cdef cl_int err_code
            cdef size_t * sizes = NULL
            cdef size_t slen = 0 
            err_code = clGetProgramInfo(self.program_id, CL_PROGRAM_BINARY_SIZES, 0, NULL, & slen)
            if err_code != CL_SUCCESS: raise OpenCLException(err_code)
            
            sizes = < size_t *> malloc(slen)
            
            err_code = clGetProgramInfo(self.program_id, CL_PROGRAM_BINARY_SIZES, slen, sizes, NULL)
            if err_code != CL_SUCCESS: 
                free(sizes)
                raise OpenCLException(err_code)
            
            size_list = []
            for i in range(slen / sizeof(size_t)):
                size_list.append(sizes[i])
            free(sizes)
            
            return size_list
        
    property binaries:
        def __get__(self):
            
            sizes = self.binary_sizes
            
            cdef size_t param_size = sizeof(char *) * len(sizes)
             
            cdef char ** binaries = < char **> malloc(param_size)
            
            for i, size in enumerate(sizes):
                if size > 0:
                    binaries[i] = < char *> malloc(sizeof(char) * size)
                else:
                    binaries[i] = NULL
                    
            err_code = clGetProgramInfo(self.program_id, CL_PROGRAM_BINARIES, 0, NULL, & param_size)
            err_code = clGetProgramInfo(self.program_id, CL_PROGRAM_BINARIES, param_size, binaries, NULL)
            
            if err_code != CL_SUCCESS:
                for i in range(len(sizes)):
                    if binaries[i] != NULL: free(binaries[i])
                free(binaries)
                raise OpenCLException(err_code)
            
            py_binaries = []
            
            for i in range(len(sizes)):
                if binaries[i] == NULL:
                    py_binaries.append(None)
                    continue
                
                binary = bytes(binaries[i][:sizes[i]])
                
                py_binaries.append(binary)
                
                free(binaries[i])
            
            free(binaries)
                
            return dict(zip(self.devices, py_binaries))
            
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
                
            return dict(zip(self.devices, logs))
                
        
    property context:
        def __get__(self):
            
            cdef cl_int err_code
            cdef cl_context ctx = NULL
            
            err_code = clGetProgramInfo(self.program_id, CL_PROGRAM_CONTEXT, sizeof(cl_context), & ctx, NULL)
              
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return CyContext_Create(ctx)
        
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

#===============================================================================
# 
#===============================================================================

cdef api int CyDevice_Check(object py_device):
    return isinstance(py_device, Device)

cdef api cl_device_id CyDevice_GetID(object py_device):
    cdef Device device = < Device > py_device
    return device.device_id

cdef api object DeviceIDAsPyDevice(cl_device_id device_id):
    cdef Device device = < Device > Device.__new__(Device)
    device.device_id = device_id
    return device



#===============================================================================
# 
#===============================================================================
cdef api object cl_eventAs_PyEvent(cl_event event_id):
    cdef Event event = < Event > Event.__new__(Event)
    clRetainEvent(event_id)
    event.event_id = event_id
    return event

cdef api cl_event cl_eventFrom_PyEvent(object event):
    return (< Event > event).event_id

cdef api object PyEvent_New(cl_event event_id):
    cdef Event event = < Event > Event.__new__(Event)
    event.event_id = event_id
    return event

cdef api int PyEvent_Check(object event):
    return isinstance(event, Event)
## ############# #### #### #### #### #### #### #### #### #### #### ####

cdef api object CyProgram_Create(cl_program program_id):
    cdef Program prog = < Program > Program.__new__(Program)
    prog.program_id = program_id
    clRetainProgram(program_id)
    return prog
