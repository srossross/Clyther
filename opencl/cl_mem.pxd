
from _cl cimport *

cdef api object MemObjectAs_pyMemoryObject(cl_mem buffer_id)

cdef api object DeviceMemoryView_New(cl_mem buffer_id, char * _format, int readonly, int ndim, 
                                     Py_ssize_t * _shape, Py_ssize_t * _strides, Py_ssize_t * _suboffsets, 
                                     Py_ssize_t itemsize)


cdef api cl_mem clMemFrom_pyMemoryObject(object memobj)
cdef api int PyMemoryObject_Check(object memobj)