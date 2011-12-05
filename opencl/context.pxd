

from _cl import *

cdef api cl_context ContextFromPyContext(object pycontext)
cdef api object ContextAsPyContext(cl_context context)

