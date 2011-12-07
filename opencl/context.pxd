

from _cl cimport *

cdef api cl_context CyContext_GetID(object pycontext)

cdef api object CyContext_Create(cl_context context)

cdef api int CyContext_Check(object context)

