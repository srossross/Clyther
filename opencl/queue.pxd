
from _cl cimport *

cdef api cl_command_queue CyQueue_GetID(object queue)
cdef api int CyQueue_Check(object queue)
cdef api object CyQueue_Create(cl_command_queue queue_id)

cdef api cl_uint _make_wait_list(wait_on, cl_event ** event_wait_list_ptr)
