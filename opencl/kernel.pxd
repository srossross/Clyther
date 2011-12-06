
from _cl cimport *

cdef api cl_kernel KernelFromPyKernel(object py_kernel)
cdef api object KernelAsPyKernel(cl_kernel kernel_id)


cdef extern from "stdarg.h":
    ctypedef struct va_list:
        pass
    ctypedef struct fake_type:
        pass
    void va_start(va_list, void* arg)
    void* va_arg(va_list, fake_type)
    void va_end(va_list)
    fake_type int_type "int"
