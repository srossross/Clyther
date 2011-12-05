
from _cl cimport *

cdef api cl_command_queue clQueueFrom_PyQueue(object queue)
cdef api object clQueueAs_PyQueue(cl_command_queue queue_id)
