# Pyrex sources to compute the laplacian.
# This code wors for both Numeric and numarray arrays and shows
# another way to access the data.
#
# Author: Prabhu Ramachandran <prabhu_r at users dot sf dot net>
# Modified by F. Alted for yet another way to access Numeric/numarray
# objects

# Some helper routines from the Python API
cdef extern from "Python.h":
  int PyObject_AsReadBuffer(object, void **rbuf, int *len)
  int PyObject_AsWriteBuffer(object, void **rbuf, int *len)
    
cdef extern from "math.h":
    double sqrt(double x)

def pyrexTimeStep(object u, double dx, double dy):
    cdef int nx, ny
    cdef double dx2, dy2, dnr_inv, err
    cdef double *elem
    cdef int i, j
    cdef double *uc, *uu, *ud, *ul, *ur
    cdef double diff, tmp
    cdef int buflen
    cdef void *data
    
    if u.typecode() <> "d":
        raise TypeError("Double array required")
    if len(u.shape) <> 2:
        raise ValueError("2 dimensional array required")

    nx = u.shape[0]
    ny = u.shape[1]
    dx2, dy2 = dx**2, dy**2
    dnr_inv = 0.5/(dx2 + dy2)
    # Get the pointer to the buffer data area
    if hasattr(u, "__class__"):
        # numarray case
        if PyObject_AsReadBuffer(u._data, &data, &buflen) <> 0:
            raise RuntimeError("Error getting the array data buffer")
    else:
        # Numeric case
        if PyObject_AsReadBuffer(u, &data, &buflen) <> 0:
            raise RuntimeError("Error getting the array data buffer")

    elem = <double *>data
    
    err = 0.0
    for i from 1 <= i < nx-1:
        uc = elem + i*ny + 1
        ur = elem + i*ny + 2
        ul = elem + i*ny
        uu = elem + (i+1)*ny + 1
        ud = elem + (i-1)*ny + 1
        
        for j from 1 <= j < ny-1:
            tmp = uc[0]
            uc[0] = ((ul[0] + ur[0])*dy2 +
                     (uu[0] + ud[0])*dx2)*dnr_inv
            diff = uc[0] - tmp
            err = err + diff*diff
            uc = uc + 1; ur = ur + 1;  ul = ul + 1
            uu = uu + 1; ud = ud + 1

    return sqrt(err)
