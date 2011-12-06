

from _cl cimport *

cdef api cl_context ContextFromPyContext(object pycontext)

cdef api object ContextAsPyContext(cl_context context)

cdef api int PyContext_Check(object context)

