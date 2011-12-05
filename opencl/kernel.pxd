
from _cl cimport *

cdef api cl_kernel KernelFromPyKernel(object py_kernel)
cdef api object KernelAsPyKernel(cl_kernel kernel_id)
