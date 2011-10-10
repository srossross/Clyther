'''

'''
from _cl cimport * 
from libc.stdio cimport printf

from libc.stdlib cimport malloc, free 
from cpython cimport PyObject, Py_DECREF, Py_INCREF 

from cpython cimport PyObject_CheckBuffer, PyBUF_WRITABLE, \
    Py_buffer, PyObject_GetBuffer, PyBuffer_Release, PyBUF_FORMAT, \
    PyBUF_SIMPLE, PyBUF_ANY_CONTIGUOUS, PyBuffer_FromReadWriteMemory, PyBuffer_FromMemory
    
    
cimport numpy as np

MAGIC_NUMBER = 0xabc123

cdef extern from * :
 
    void PyEval_InitThreads()
    PyObject * PyMemoryView_FromBuffer(Py_buffer *) 
    int PyObject_AsReadBuffer(PyObject * , void ** , Py_ssize_t *) except -1
    int PyObject_CheckReadBuffer(PyObject *)
    
PyEval_InitThreads()

OpenCLErrorStrings = {
                
    CL_INVALID_CONTEXT: 'Context is not a valid context.',
    CL_INVALID_VALUE: 'Values specified in flags are not valid as defined in table 5.3.',
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
                }


def as_mem_view(np.ndarray array not None):
    
#    cdef np.PyArrayObject * a = np.PyArray_FromAny(array)
    
    print array

def from_memory_view(memory_view):
    
    memory_view

class OpenCLException(Exception):
    def __init__(self, err_code, mapping=None):
        if mapping is None:
            mapping = OpenCLErrorStrings
        Exception.__init__(self, err_code, mapping.get(err_code, 'Uknown OpenCL error'))

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


cdef class Context:
    cdef cl_context context_id
    
    def __init__(self, devices=(), device_type=None, platform=None):
        
        cdef cl_context_properties * properties = NULL
        
        cdef cl_device_type dtype
        cdef cl_int err_code
        cdef cl_uint num_devices
        cdef cl_device_id * _devices

        if type is not None:
            dtype = < cl_device_type > device_type
            self.context_id = clCreateContextFromType(properties, device_type, NULL, NULL, & err_code)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
        else:
            num_devices = len(devices)
            _devices = < cl_device_id *> malloc(num_devices * sizeof(cl_device_id))
            
            for i in range(num_devices): 
                _devices[i] = (< Device > devices[i]).device_id
                 
            self.context_id = clCreateContext (properties, num_devices, _devices, NULL, NULL, & err_code)
            free(_devices)

            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)

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
    
    def enqueue_read_buffer(self, buffer, host_destination, size_t offset=0, size=None, blocking=False, events=None):
        
        cdef cl_int err_code
        cdef Py_buffer view

        cdef cl_bool blocking_read = 1 if blocking else 0
        cdef void * ptr = NULL
        cdef cl_uint num_events_in_wait_list = 0
        cdef cl_event * event_wait_list = NULL
        cdef Event event = Event()   
        cdef size_t cb   
        cdef cl_mem buffer_id = (< Buffer > buffer).buffer_id

        if PyObject_GetBuffer(host_destination, & view, PyBUF_SIMPLE | PyBUF_ANY_CONTIGUOUS):
            raise ValueError("argument 'host_buffer' must be a readable buffer object")
        
        if size is None:
            cb = min(view.len, buffer.size)
            
        if view.len < size:
            raise Exception("destination (host) buffer is too small")
        elif buffer.size < size:
            raise Exception("source (device) buffer is too small")
        
        ptr = view.buf
        
        if events:
            num_events_in_wait_list = len(events)
            event_wait_list = < cl_event *> malloc(num_events_in_wait_list * sizeof(cl_event))
            
            for i in range(num_events_in_wait_list):
                tmp_event = < Event > events[i]
                event_wait_list[i] = tmp_event.event_id
            
        err_code = clEnqueueReadBuffer (self.queue_id, buffer_id,
                                        blocking_read, offset, cb, ptr,
                                        num_events_in_wait_list, event_wait_list, & event.event_id)
    
        if event_wait_list != NULL:
            free(event_wait_list)
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)

        if not blocking:
            return event
        
    def enqueue_map_buffer(self, buffer, blocking=False, size_t offset=0, size=None, events=None, read=True, write=True, format="B", itemsize=1):
        
        cdef void * host_buffer = NULL
        cdef cl_mem _buffer
        cdef cl_bool blocking_map = 1 if blocking else 0
        cdef cl_map_flags map_flags = 0
        cdef size_t cb = 0
        cdef cl_uint num_events_in_wait_list = 0
        cdef cl_event * event_wait_list = NULL
        cdef Event event
        cdef cl_int err_code
        
        if read:
            map_flags |= CL_MAP_READ
        if write:
            map_flags |= CL_MAP_WRITE
            
        

        _buffer = (< Buffer > buffer).buffer_id
        
        if size is None:
            cb = buffer.size - offset
        else:
            cb = < size_t > size
            
            
#        cdef Py_buffer * view = < Py_buffer *> malloc(sizeof(Py_buffer)) 
#        
#        cdef char * _format = < char *> format
#        view.itemsize = itemsize
#        
#        if not view.itemsize:
#            raise Exception()
#        if (cb % view.itemsize) != 0:
#            raise Exception("size-offset must be a multiple of itemsize of format %r (%i)" % (format, view.itemsize))

        if events:
            num_events_in_wait_list = len(events)
            event_wait_list = < cl_event *> malloc(num_events_in_wait_list * sizeof(cl_event))
            
            for i in range(num_events_in_wait_list):
                tmp_event = < Event > events[i]
                event_wait_list[i] = tmp_event.event_id
                
        
        host_buffer = clEnqueueMapBuffer (self.queue_id, _buffer, blocking_map, map_flags,
                                          offset, cb, num_events_in_wait_list, event_wait_list,
                                          & event.event_id, & err_code)
#        print "clEnqueueMapBuffer"
        
        
        if event_wait_list != NULL:
            free(event_wait_list)
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)

        if host_buffer == NULL:
            raise Exception("host buffer is null")
        
        if write:
            memview = < object > PyBuffer_FromReadWriteMemory(host_buffer, cb)
        else:
            memview = < object > PyBuffer_FromMemory(host_buffer, cb)
            
#        view.buf = host_buffer
#        view.len = cb
#        view.readonly = 0 if write else 1
#        view.format = _format
#        view.ndim = 1
#        view.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t))
#        view.shape[0] = cb / view.itemsize 
#        view.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t))
#        view.strides[0] = 1
#        view.suboffsets = < Py_ssize_t *> malloc(sizeof(Py_ssize_t))
#        view.suboffsets[0] = 0
#         
#        view.internal = NULL 
#         
#        
        
        
        if not blocking:
            return (memview, event)
        else:
            return (memview, None)
        
    def enqueue_unmap(self, memobject, buffer, events=None,):

        cdef void * mapped_ptr = NULL
        cdef cl_mem memobj = NULL 
        cdef cl_uint num_events_in_wait_list = 0
        cdef cl_event * event_wait_list = NULL
        cdef Event event = Event()
        
        cdef cl_int err_code
        memobj = (< Buffer > memobject).buffer_id
        cdef Py_ssize_t buffer_len
        
        PyObject_AsReadBuffer(< PyObject *> buffer, & mapped_ptr, & buffer_len)

        if events:
            num_events_in_wait_list = len(events)
            event_wait_list = < cl_event *> malloc(num_events_in_wait_list * sizeof(cl_event))
            
            for i in range(num_events_in_wait_list):
                tmp_event = < Event > events[i]
                event_wait_list[i] = tmp_event.event_id
                
        err_code = clEnqueueUnmapMemObject(self.queue_id, memobj, mapped_ptr, num_events_in_wait_list,
                                        event_wait_list, & event.event_id)
        
        if event_wait_list != NULL:
            free(event_wait_list)
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
        
        return event
    
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

cdef class Event:
    cdef cl_event event_id

    def wait(self):
        
        cdef cl_int err_code
        
        err_code = clWaitForEvents(1, & self.event_id)
    
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)


cdef extern from * :
    ctypedef Py_ssize_t (*readbufferproc)(PyObject * self, Py_ssize_t segment, void ** ptrptr)
    
    cdef readbufferproc emit_buffer_proc "__pyx_v_py_buffer->ob_type->tp_as_buffer->bf_getreadbuffer; //" ()
    
class CLMapContext(object):
    def __init__(self, queue, dev_buffer, size_t offset=0, size=None, events=None, read=True, write=True):
        self.queue = queue
        self.dev_buffer = dev_buffer
        self.offset = offset
        self.size = size
        self.events = events
        self.read = read
        self.write = write
        
    def __enter__(self):
        self.buffer, _ = self.queue.enqueue_map_buffer(self.dev_buffer, blocking=True,
                                                       offset=self.offset, size=self.size,
                                                       events=self.events, read=self.read, write=self.write)
        
        return self.buffer
    
    def __exit__(self, type, value, traceback):
        event = self.queue.enqueue_unmap(self.dev_buffer, self.buffer)
        event.wait()
        
cdef class Buffer:
    cdef cl_mem buffer_id
    cdef size_t _size
    
    def map(self, queue, size_t offset=0, size=None, events=None, read=True, write=True):
        return CLMapContext(queue, self, offset, size, events, read, write)
    
    def __dealloc__(self):
        cdef cl_int err_code
        
        if self.buffer_id != NULL:
            err_code = clReleaseMemObject(self.buffer_id)
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
 
        self.buffer_id = NULL
        
    def __init__(self, Context ctx, size=None, read_only=False, host_buffer=None, use_host=False, alloc_host=False, copy=False):
        
        self.buffer_id = NULL
        cdef cl_mem_flags flags = 0
        cdef Py_buffer view
        
        cdef cl_int err_code
        cdef void * host_ptr = NULL 
        cdef PyObject * py_buffer
        cdef long long py_size 
        
        cdef readbufferproc buffproc = NULL
        if read_only:
            flags |= CL_MEM_READ_ONLY
        else:
            flags |= CL_MEM_READ_WRITE
        
        if  use_host or alloc_host or copy:
                   
#            if isinstance(host_buffer, buffer):
#                
#                py_buffer = <PyObject *> buffer
#                
#                print "emit_buffer_proc"
#                buffproc = emit_buffer_proc()
#                print "done"
#                
#                if buffproc == NULL:
#                    raise ValueError("argument 'host_buffer' must be a readable buffer object")
#                
#                py_size = buffproc(py_buffer, 0, &host_ptr)
#                
#                if py_size == -1 :
#                    raise ValueError("Error getting buffer proc")
#                if py_size < size:
#                    raise ValueError("size of buffer should be greater to or equal the size argument")
#                
#                print py_size,
            # else 
            if 1:
                if PyObject_GetBuffer(host_buffer, & view, PyBUF_SIMPLE | PyBUF_ANY_CONTIGUOUS):
                    raise ValueError("argument 'host_buffer' must be a readable buffer object")
                
                if size is None:
                    size = view.len
                elif view.len < size:
                    raise ValueError("size of buffer should be greater to or equal the size argument")
            
            if use_host:
                flags |= CL_MEM_USE_HOST_PTR
            if alloc_host:
                flags |= CL_MEM_ALLOC_HOST_PTR
            if copy:
                flags |= CL_MEM_COPY_HOST_PTR
            host_ptr = view.buf
            
        self._size = < size_t > size
        
        self.buffer_id = clCreateBuffer(ctx.context_id, flags, size, host_ptr, & err_code)

        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)

    property size:
        def __get__(self):
            return self._size

    def _sizeof(self):
        return sizeof(cl_mem)
    
    def _addressof(self):
        return < size_t > & self.buffer_id
    
    def __getitem__(self, item):
        
        cdef cl_int err_code
        cdef cl_mem_flags flags = 0
        cdef cl_mem new_buffer = NULL
        
        flags |= CL_MEM_READ_WRITE
        
        cdef _cl_buffer_region info
        
        if isinstance(item, slice):
            
            start, stop, step = item.indices(self.size)
            if step != 1:
                raise Exception("can not handle non-contiguous step_size")
            info.origin = start
            info.size = stop - start
            
            new_buffer = clCreateSubBuffer(self.buffer_id, flags, CL_BUFFER_CREATE_TYPE_REGION, < void *> & info, & err_code)
            
            return MemObject_AsPyCLBuffer(new_buffer, info.size)
        else:
            raise Exception("not a slice")
    
cdef class Image:
    pass

cdef class Program:
    cdef cl_program program_id
    
    def __cinit__(self, Context context, source=None):
        
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
        
        err_code = clBuildProgram (self.program_id, num_devices, device_list, _options, NULL, NULL)
        
        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)

        return self
    
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
            raise OpenCLException(err_code)
        
        return KernelAsPyKernel(kernel_id)

    property devices:
        def __get__(self):
            
            cdef cl_int err_code
            cdef cl_uint num_devices
            cdef cl_device_id * device_list
            
            err_code = clGetProgramInfo (self.program_id, CL_PROGRAM_NUM_DEVICES, sizeof(cl_uint), & num_devices, NULL)
              
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            device_list = < cl_device_id *> malloc(sizeof(cl_device_id) * num_devices)
            err_code = clGetProgramInfo (self.program_id, CL_PROGRAM_DEVICES, sizeof(cl_device_id) * num_devices, device_list, NULL)
            
            if err_code != CL_SUCCESS:
                free(device_list)
                raise OpenCLException(err_code)
            
            free(device_list)
            
            devices = []
            
            for i in range(num_devices):
                devices.append(DeviceIDAsPyDevice(device_list[i]))
                
            return devices
        

cdef class Kernel:
    cdef cl_kernel kernel_id
    cdef object _argtypes
    cdef object _argnames 
    
    def __cinit__(self):
        self._argtypes = None
        self._argnames = None
        
    property argtypes:
        def __get__(self):
            return self._argtypes
        
        def __set__(self, value):
            self._argtypes = tuple(value)
    property argnames:
        def __get__(self):
            return self._argnames
        
        def __set__(self, value):
            self._argnames = tuple(value)
            
    def _format_args(self, *args, **kwargs):
        if kwargs and not self._argnames:
            raise Exception("Argnames not set. can not use keyword arguemnts")
        
        if self.argnames or self.argtypes:
            num_args = len(self.argtypes) if self.argtypes else self.argnames
        else:
            num_args = len(args)
          
        defined = set(range(len(args)))
        if self.argnames:
            defined |= set(self.argnames.index(name) for name in kwargs.keys())
            
        undefined = defined - set(range(num_args))
        if undefined:
            idx = undefined.pop()
            if self.argnames:
                raise Exception('argument %r at position %i undefined' % (self.argnames[idx], idx))
            else:
                raise Exception('argument at position %i undefined' % (idx))
         
        arg_list = [None for _ in range(num_args)]
        
        for i, arg in enumerate(args):
            if self.argtypes:
                arg_list[i] = self.argtypes[i](args[i])
            else:
                arg_list[i] = args[i]
        
        for name, value in kwargs.items():
            
            if name not in self.argnames:
                raise Exception()
            
            idx = self.argnames.index(name)
            
            if idx < len(args):
                raise Exception("arg specified in both kwrags and args")
            
            if self.argtypes:
                arg_list[idx] = self.argtypes[idx](value)
            else:
                arg_list[idx] = value
                
        return tuple(arg_list)
        
    def __call__(self, *args, **kwargs):
        pass
    

## API FUNCTIONS #### #### #### #### #### #### #### #### #### #### ####
## ############# #### #### #### #### #### #### #### #### #### #### ####
cdef api cl_context ContextFromPyContext(object pycontext):
    cdef Context context = < Context > pycontext
    return context.context_id

cdef api object ContextAsPyContext(cl_context context):
    ctx = < Context > Context.__new__()
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
    return kernel

#===============================================================================
# 
#===============================================================================
cdef api cl_mem MemObject_FromPyCLBuffer(object py_buffer, size_t *size):
    cdef Buffer buffer = <Buffer> py_buffer
    size[0] = buffer._size 
    return buffer.buffer_id

cdef api object MemObject_AsPyCLBuffer(cl_mem buffer_id, size_t size):
    cdef Buffer buffer = < Buffer > Buffer.__new__(Buffer)
    buffer.buffer_id = buffer_id
    buffer._size = size
    return buffer

## ############# #### #### #### #### #### #### #### #### #### #### ####

