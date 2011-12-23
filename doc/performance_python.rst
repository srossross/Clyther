========================
Performance Python
========================


A beginners guide to using Python for performance computing
-----------------------------------------------------------------

This is an extension of the original article written by Prabhu Ramachandran. The original article can be found `here <http://www.scipy.org/PerformancePython>_`.
 
A comparison of weave with NumPy, Cython, opencl, and CLyther for solving Laplace's equation. 
laplace.py is the complete Python code discussed below. The source tarball ( perfpy_2.tgz ) contains in addition the Fortran code, the pure C++ code, the Pyrex sources 
and a setup.py script to build the f2py and Pyrex module.

Introduction
---------------

This is a simple introductory document to using Python for performance computing. We'll use NumPy, SciPy's weave (using both weave.blitz and weave.inline) and Pyrex. 
We will also show how to use f2py to wrap a Fortran subroutine and call it from within Python.
We will also use this opportunity to benchmark the various ways to solve a particular numerical problem in Python and compare them to an implementation of the algorithm in C++.

Problem description
-------------------------
The example we will consider is a very simple (read, trivial) case of solving the 2D Laplace equation using an iterative finite difference 
scheme (four point averaging, Gauss-Seidel or Gauss-Jordan). The formal specification of the problem is as follows. We are required to solve 
for some unknown function u(x,y) such that 2u = 0 with a boundary condition specified. For convenience the domain of interest is considered 
to be a rectangle and the boundary values at the sides of this rectangle are given.

It can be shown that this problem can be solved using a simple four point averaging scheme as follows. Discretise the domain into an (nx x ny) grid of points.
Then the function u can be represented as a 2 dimensional array - u(nx, ny). The values of u along the sides of the rectangle are given. The solution can be 
obtained by iterating in the following manner::

    for i in range(1, nx-1):
        for j in range(1, ny-1):
            u[i,j] = ((u[i-1, j] + u[i+1, j])*dy**2 +
                      (u[i, j-1] + u[i, j+1])*dx**2)/(2.0*(dx**2 + dy**2))


Task Parallel
-------------------


Task Parallel::

    @cly.task
    def cly_time_step_task(u, dy2, dx2, dnr_inv):

        nx = u.shape[0] 
        ny = u.shape[1]
        
        for i in range(1, nx - 1):
            for j in range(1, ny - 1):
                u[i, j] = ((u[i - 1, j] + u[i + 1, j]) * dy2 + 
                          (u[i, j - 1] + u[i, j + 1]) * dx2) * dnr_inv
    
Data Parallel
-------------------

Data Parallel::

    @cly.global_work_size(lambda u: [u.shape[0] - 2])
    @cly.kernel
    def lp2dstep(u, dx2, dy2, dnr_inv, stidx):
        i = clrt.get_global_id(0) + 1
        
        ny = u.shape[1]
        
        for j in range(1 + ((i + stidx) % 2), ny - 1, 2):
            u[j, i] = ((u[j - 1, i] + u[j + 1, i]) * dy2 + 
                       (u[j, i - 1] + u[j, i + 1]) * dx2) * dnr_inv
