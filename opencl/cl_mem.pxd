
from _cl cimport *

cdef api object CyMemoryObject_Create(cl_mem buffer_id)

cdef api int CyView_GetBuffer(object view, Py_buffer* buffer)
    
cdef api object CyView_Create(cl_mem buffer_id, Py_buffer* buffer, int incref)

cdef api int CyMemoryObject_Check(object memobj)

cdef api cl_mem CyMemoryObject_GetID(object memobj)

