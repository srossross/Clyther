
import ctypes
from opencl._errors import OpenCLException
from opencl._cl_mem import MemoryObject
from inspect import isfunction
from opencl.type_formats import refrence, ctype_from_format, type_format, cdefn

from libc.stdlib cimport malloc, free
from _cl cimport *
from opencl.cl_mem cimport clMemFrom_pyMemoryObject

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
        cdef cl_mem buffer = clMemFrom_pyMemoryObject(memobj)
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
        cdef cl_mem mem_id
        for arg_index, (argtype, arg) in enumerate(zip(self._argtypes, args)):
            carg = argtype(arg)
            if isinstance(argtype, global_memory):
                arg_size = sizeof(cl_mem)
                mem_id = clMemFrom_pyMemoryObject(arg)
                arg_value = < void *> & mem_id
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
    

#===============================================================================
# API
#===============================================================================
cdef api cl_kernel KernelFromPyKernel(object py_kernel):
    cdef Kernel kernel = < Kernel > py_kernel
    return kernel.kernel_id

cdef api object KernelAsPyKernel(cl_kernel kernel_id):
    cdef Kernel kernel = < Kernel > Kernel.__new__(Kernel)
    kernel.kernel_id = kernel_id
    clRetainKernel(kernel_id)
    return kernel
