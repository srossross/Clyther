import struct
from opencl.errors import OpenCLException

from _cl cimport *
from clgl cimport *

from libc.stdlib cimport malloc, free 
from cpython cimport PyObject, Py_DECREF, Py_INCREF, PyBuffer_IsContiguous, PyBuffer_FillContiguousStrides
from cpython cimport Py_buffer, PyBUF_SIMPLE, PyBUF_STRIDES, PyBUF_ND, PyBUF_FORMAT, PyBUF_INDIRECT, PyBUF_WRITABLE

from opencl.cl_mem cimport DeviceMemoryView_New
from opencl.context cimport ContextFromPyContext

def empty_gl(context, shape, ctype='B'):
    
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
       
    cdef GLuint vbo 
    glGenBuffers(1, & vbo)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    
    cdef GLsizeiptr nbytes = itemsize
    for i in shape:
        nbytes *= i
                
    glBufferData(GL_ARRAY_BUFFER, nbytes, NULL, GL_STATIC_DRAW)
    
    if glGetError() != GL_NO_ERROR:
        raise Exception("OpenGL error")
    
    cdef cl_mem buffer_id = clCreateFromGLBuffer(ctx, flags, vbo, & err_code)
    
    
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    
    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)

    
    cdef int readonly = 0
    cdef int ndim = len(shape)
    
    cdef Py_ssize_t * _shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
    cdef Py_ssize_t * _strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
    cdef Py_ssize_t * _suboffsets = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * ndim)
    
    for i in range(ndim):
        _shape[i] = shape[i]
        _suboffsets[i] = 0
    
    PyBuffer_FillContiguousStrides(ndim, _shape, _strides, itemsize, 'C')
    
    buffer = DeviceMemoryView_New(buffer_id, format, readonly, ndim, _shape, _strides, _suboffsets, itemsize)

    return buffer

