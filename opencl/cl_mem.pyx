import weakref
import struct
import ctypes

from opencl.errors import OpenCLException

from libc.stdlib cimport malloc, free 
from cpython cimport PyObject, Py_DECREF, Py_INCREF, PyBuffer_IsContiguous, PyBuffer_FillContiguousStrides
from cpython cimport Py_buffer, PyBUF_SIMPLE, PyBUF_STRIDES, PyBUF_ND, PyBUF_FORMAT, PyBUF_INDIRECT, PyBUF_WRITABLE

from _cl cimport *
from opencl.context cimport ContextFromPyContext, ContextAsPyContext
from opencl.queue cimport CyQueue_GetID, CyQueue_Create



cdef extern from "Python.h":

    object PyByteArray_FromStringAndSize(char * , Py_ssize_t)
    object PyMemoryView_FromBuffer(Py_buffer * info)
    int PyObject_GetBuffer(object obj, Py_buffer * view, int flags)
    int PyObject_CheckBuffer(object obj)
    void PyBuffer_Release(Py_buffer * view)


cdef class MemoryObject:
    cdef cl_mem buffer_id
    
    def get_buffer_id(self):
        return <size_t>self.buffer_id
        
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
            err_code = clGetMemObjectInfo(self.buffer_id, CL_MEM_REFERENCE_COUNT, sizeof(cl_uint),
                                           < void *>& param_value, NULL)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)

            return param_value

    property _mapcount:
        def __get__(self):
            
            cdef cl_uint param_value
            cdef cl_int err_code
            err_code = clGetMemObjectInfo(self.buffer_id, CL_MEM_MAP_COUNT, sizeof(cl_uint),
                                          < void *>& param_value, NULL)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)

            return param_value
    
    property base:
        def __get__(self):
            cdef cl_mem param_value
            cdef cl_int err_code
            
            err_code = clGetMemObjectInfo(self.buffer_id, CL_MEM_ASSOCIATED_MEMOBJECT, sizeof(cl_mem), < void *>& param_value, NULL)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            if param_value == NULL:
                return None
            else:
                return CyMemoryObject_Create(param_value)
    
    
cdef class DeviceMemoryView(MemoryObject):
    
    cdef Py_buffer *buffer    
#    cdef char * _format
#    cdef public int readonly
#    cdef public int ndim
#    cdef Py_ssize_t * _shape
#    cdef Py_ssize_t * _strides
#    cdef Py_ssize_t * _suboffsets
#    cdef public Py_ssize_t itemsize
    cdef object __weakref__
    
    def __cinit__(self):
        self.buffer = NULL
        
    def __init__(self, context, size_t size, cl_mem_flags flags=CL_MEM_READ_WRITE):
        
        cdef cl_context ctx = ContextFromPyContext(context)
        
        self.buffer_id = NULL 
        cdef void * host_ptr = NULL
        cdef cl_int err_code
        self.buffer_id = clCreateBuffer(ctx, flags, size, host_ptr, & err_code)

        if err_code != CL_SUCCESS:
            raise OpenCLException(err_code)
    
    property ndim:
        def __get__(self):
            return self.buffer.ndim

    property readonly:
        def __get__(self):
            return self.buffer.readonly
        
    property itemsize:
        def __get__(self):
            return self.buffer.itemsize
        
    property format:
        def __get__(self):
            if self.buffer.format != NULL:
                return str(self.buffer.format)
            else:
                return "B"
        
    property shape:
        def __get__(self):
            shape = []
            for i in range(self.buffer.ndim):
                shape.append(self.buffer.shape[i])
            return tuple(shape)

    property suboffsets:
        def __get__(self):
            
            if self.buffer.suboffsets == NULL:
                return None
            
            suboffsets = []
            for i in range(self.buffer.ndim):
                suboffsets.append(self.buffer.suboffsets[i])
            return tuple(suboffsets)

    property strides:
        def __get__(self):
            strides = []
            for i in range(self.buffer.ndim):
                strides.append(self.buffer.strides[i])
            return tuple(strides)
        
    def map(self, queue, blocking=True, readonly=False, size_t offset=0, size_t size=0):
        
        cdef cl_map_flags flags = CL_MAP_READ
        
        if not readonly: 
            flags |= CL_MAP_WRITE
        
        cdef cl_bool blocking_map = 1 if blocking else 0
        if size == 0:
            size = self.mem_size
            
        return MemoryViewMap(queue, self, blocking_map, flags, offset, size)

    @classmethod
    def from_host(cls, context, host):
        
        cdef cl_context ctx = ContextFromPyContext(context)
         
        cdef Py_buffer view
        cdef Py_buffer *buffer = <Py_buffer*>malloc(sizeof(Py_buffer))
        cdef cl_mem buffer_id = NULL
        
        cdef int py_flags = PyBUF_SIMPLE | PyBUF_STRIDES | PyBUF_ND | PyBUF_FORMAT
        
        cdef cl_mem_flags mem_flags = CL_MEM_COPY_HOST_PTR | CL_MEM_READ_WRITE
        cdef cl_int err_code
         
        if not PyObject_CheckBuffer(host):
            raise Exception("argument host must support the buffer protocal (got %r)" % host)
        
        if PyObject_GetBuffer(host, & view, py_flags) < 0:
            raise Exception("argument host must support the buffer protocal (got %r)" % host)
            
        if PyBuffer_IsContiguous(& view, 'C'):
            
            buffer_id = clCreateBuffer(ctx, mem_flags, view.len, view.buf, & err_code)
            
            PyBuffer_Release(& view)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            buffer.format = view.format
            buffer.readonly = 1
            buffer.itemsize = view.itemsize
            buffer.ndim = view.ndim
            
            buffer.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * view.ndim)
            buffer.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * view.ndim)
            buffer.suboffsets = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * view.ndim)
            
            for i in range(view.ndim):
                buffer.shape[i] = view.shape[i]
                buffer.strides[i] = view.strides[i]
                buffer.suboffsets[i] = 0

            return CyView_Create(buffer_id, buffer, 0)
        else:
            raise NotImplementedError("data must be contiguous")
        

    def __getitem__(self, args):
        
        if not isinstance(args, tuple):
            args = (args,)
            
        if len(args) != self.buffer.ndim:
            raise IndexError("too many indices expected %i (got %i)" % (self.buffer.ndim, len(args)))
        
        ndim = self.buffer.ndim
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
        
        cdef Py_buffer *buffer = <Py_buffer *> malloc(sizeof(Py_buffer)) 
        
#        buffer.buffer_id = self.buffer_id
        
        buffer.format = self.buffer.format
        buffer.readonly = self.readonly
        buffer.itemsize = self.buffer.itemsize
        buffer.ndim = ndim
        
        buffer.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
        buffer.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
        buffer.suboffsets = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
        
        for i in range(ndim):
            buffer.shape[i] = shape[i]
            buffer.strides[i] = strides[i]
            buffer.suboffsets[i] = suboffsets[i]
        
        return CyView_Create(self.buffer_id, buffer, 1)
    
    property size:
        def __get__(self):
            shape = self.shape
            size = 1
            for i in range(self.buffer.ndim):
                size *= shape[i]
            return size

    property nbytes:
        def __get__(self):
            return self.size * self.buffer.itemsize

    property offset:
        def __get__(self):
            cdef size_t offset = 0
            
            for i in range(self.buffer.ndim):
                offset += self.buffer.suboffsets[i]
                
            return offset

    def __len__(self):
        return self.size 
            
    property is_contiguous:
        def __get__(self):
            
            strides = [self.buffer.itemsize]
            for i in range(self.buffer.ndim - 1):
                stride = strides[i]
                size = self.shape[-i - 1]
                strides.append(stride * size)
                
            return self.strides == tuple(strides[::-1])
        
    def copy(self, queue):
        
        cdef size_t src_row_pitch = 0   
        cdef size_t src_slice_pitch = 0 
        cdef size_t dst_row_pitch = 0
        cdef size_t dst_slice_pitch = 0
        
        dest = empty(self.context, self.shape, ctype=self.format)
        
        
        if self.is_contiguous:
            queue.enqueue_copy_buffer(self, dest, self.offset, dst_offset=0, size=self.nbytes, wait_on=())
            
        elif any(stride < 0 for stride in self.strides):
            raise NotImplementedError("stride < 0")
        
        elif self.buffer.ndim == 1:
            src_row_pitch = self.buffer.strides[0]
            src_slice_pitch = 0 
            dst_row_pitch = 0
            dst_slice_pitch = 0
            
            region = (dest.itemsize, dest.size, 1)
            src_origin = (self.offset, 0, 0)
            dst_origin = (0, 0, 0)
            
            queue.enqueue_copy_buffer_rect(self, dest, region, src_origin, dst_origin,
                                           src_row_pitch, src_slice_pitch,
                                           dst_row_pitch, dst_slice_pitch, wait_on=())
        elif self.buffer.ndim == 2:
            
            shape2 = self.buffer.itemsize
            shape1 = self.buffer.shape[1]
            shape0 = self.buffer.shape[0]
            
            src_row_pitch = self.buffer.strides[1]
            src_slice_pitch = self.buffer.strides[0] 

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
            
    def __releasebuffer__(self, Py_buffer * view):
        pass

def empty(context, shape, ctype='B'):
    
    cdef cl_context ctx = ContextFromPyContext(context)

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
        
    cdef cl_mem buffer_id = clCreateBuffer(ctx, flags, size, NULL, & err_code)

    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)

    cdef Py_buffer *buffer = <Py_buffer *>malloc(sizeof(Py_buffer))
    
    buffer.format = format
    buffer.readonly = 0
    buffer.itemsize = itemsize
    buffer.ndim = len(shape)
    
    buffer.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer.suboffsets = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    
    strides = [buffer.itemsize]
    for i in range(buffer.ndim):
        buffer.shape[i] = shape[i]
        buffer.suboffsets[i] = 0
    
    PyBuffer_FillContiguousStrides(buffer.ndim, buffer.shape, buffer.strides, buffer.itemsize, 'C')
    
    return CyView_Create(buffer_id, buffer, 0)
    
cdef class MemoryViewMap:
    
    cdef cl_command_queue command_queue
#    cdef DeviceMemoryView dview
    cdef public object dview
    
    cdef cl_bool blocking_map
    cdef cl_map_flags map_flags
    cdef size_t offset
    cdef size_t cb
    cdef void * bytes 
        
    def __init__(self, queue, dview, cl_bool blocking_map, cl_map_flags map_flags, size_t offset, size_t cb):
        
        self.dview = weakref.ref(dview)
        
        self.command_queue = CyQueue_GetID(queue)
        
        self.blocking_map = blocking_map
        self.map_flags = map_flags
        self.offset = offset
        self.cb = cb
    
    def __enter__(self):
        cdef void * bytes 
        cdef cl_uint num_events_in_wait_list = 0
        cdef cl_event * event_wait_list = NULL
        
        cdef cl_int err_code
        
        cdef cl_mem memobj = CyMemoryObject_GetID(self.dview())
        
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
        
        cdef Py_buffer buffer
        
        CyView_GetBuffer(self.dview(), &buffer)
        
        cdef cl_mem memobj = CyMemoryObject_GetID(self.dview())
        writable = bool(self.map_flags & CL_MAP_WRITE)

        view.readonly = 0 if writable else 1 
        
        view.format = buffer.format
        view.ndim = buffer.ndim
        view.shape = buffer.shape
        view.itemsize = buffer.itemsize
        view.internal = NULL
        view.strides = buffer.strides
        view.suboffsets = NULL
        
        cdef size_t offset = self.dview().offset 
        
        view.buf = self.bytes + offset
        
    def __releasebuffer__(self, Py_buffer * view):
        pass
    
cdef class Image(MemoryObject):
    pass


#===============================================================================
# 
#===============================================================================

cdef api object CyMemoryObject_Create(cl_mem buffer_id):
    cdef MemoryObject cview = < MemoryObject > MemoryObject.__new__(MemoryObject)
    clRetainMemObject(buffer_id)
    cview.buffer_id = buffer_id
    return cview

cdef api int CyView_GetBuffer(object view, Py_buffer* buffer):
    cdef DeviceMemoryView dview = < DeviceMemoryView > view
    buffer[0] = dview.buffer[0]
    return 0

    
cdef api object CyView_Create(cl_mem buffer_id, Py_buffer* buffer, int incref):
    cdef DeviceMemoryView dview = < DeviceMemoryView > DeviceMemoryView.__new__(DeviceMemoryView)
    if incref:
        clRetainMemObject(buffer_id)
        
    dview.buffer_id = buffer_id
    dview.buffer = buffer
    
    return dview


cdef api int CyMemoryObject_Check(object memobj):
    return isinstance(memobj, MemoryObject)

cdef api cl_mem CyMemoryObject_GetID(object memobj):
    obj = (< MemoryObject > memobj)
    cdef cl_mem buffer_id = obj.buffer_id
    return buffer_id

