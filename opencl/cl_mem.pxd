
from _cl cimport *

cdef api object MemObjectAs_pyMemoryObject(cl_mem buffer_id)

cdef api cl_mem clMemFrom_pyMemoryObject(object memobj)