#!/usr/bin/env python

"""
This script compares different ways of implementing an iterative
procedure to solve Laplace's equation.  These provide a general
guideline to using Python for high-performance computing and also
provide a simple means to compare the computational time taken by the
different approaches.  The script compares functions implemented in
pure Python, Numeric, weave.blitz, weave.inline, fortran (via f2py)
and Pyrex.  The function main(), additionally accelerates the pure
Python version using Psyco and provides some numbers on how well that
works.  To compare all the options you need to have Numeric, weave,
f2py, Pyrex and Psyco installed.  If Psyco is not installed the script
will print a warning but will perform all other tests.

The fortran and pyrex modules are compiled using the setup.py script
that is provided with this file.  You can build them like so:

  python setup.py build_ext --inplace


Author: Prabhu Ramachandran <prabhu_r at users dot sf dot net>
License: BSD
Last modified: Sep. 18, 2004
"""

import numpy
from scipy import weave
import sys, time
from argparse import ArgumentParser, FileType

from core import TimeSteper, available, timestep_methods

import opencl_methods

try:
    import flaplace
    import flaplace90_arrays
    import flaplace95_forall
except ImportError:
    flaplace = None
    flaplace90_arrays = None
    flaplace95_forall = None
try:
    import pyx_lap
except ImportError:
    pyx_lap = None

@available(True)
class slow(TimeSteper):
    'slow'
    @classmethod
    def time_step(cls, grid, dt=0.0):
        """pure-python
        Takes a time step using straight forward Python loops.
        """
        g = grid
        nx, ny = g.u.shape        
        dx2, dy2 = g.dx ** 2, g.dy ** 2
        dnr_inv = 0.5 / (dx2 + dy2)
        u = g.u
    
        err = 0.0
        for i in range(1, nx - 1):
            for j in range(1, ny - 1):
                tmp = u[i, j]
                u[i, j] = ((u[i - 1, j] + u[i + 1, j]) * dy2 + 
                          (u[i, j - 1] + u[i, j + 1]) * dx2) * dnr_inv
                diff = u[i, j] - tmp
                err += diff * diff
    
        return numpy.sqrt(err)
        
@available(True)
class numeric(TimeSteper):
    'numpy'
    @classmethod
    def time_step(cls, grid, dt=0.0):
        """
        Takes a time step using a numeric expressions."""
        g = grid
        dx2, dy2 = g.dx ** 2, g.dy ** 2
        dnr_inv = 0.5 / (dx2 + dy2)
        u = g.u
        g.old_u = u.copy()
    
        # The actual iteration
        u[1:-1, 1:-1] = ((u[0:-2, 1:-1] + u[2:, 1:-1]) * dy2 + 
                         (u[1:-1, 0:-2] + u[1:-1, 2:]) * dx2) * dnr_inv
        
        return g.computeError()


@available(True)
class weave_blitz(TimeSteper):
    'weave-blitz'
    
    @classmethod
    def time_step(cls, grid, dt=0.0):
        """weave-blitz
        Takes a time step using a numeric expression that has been
        blitzed using weave."""        
        g = grid
        dx2, dy2 = g.dx ** 2, g.dy ** 2
        dnr_inv = 0.5 / (dx2 + dy2)
        u = g.u
        g.old_u = u.copy()
    
        # The actual iteration
        expr = "u[1:-1, 1:-1] = ((u[0:-2, 1:-1] + u[2:, 1:-1])*dy2 + "\
               "(u[1:-1,0:-2] + u[1:-1, 2:])*dx2)*dnr_inv"
        weave.blitz(expr, check_size=0)
    
        return g.computeError()
    
@available(True)
class weave_fast_inline(TimeSteper):
    'weave-fast-inline'
    
    @classmethod
    def time_step(cls, grid, dt=0.0):
        """weave-fast-inline
        Takes a time step using inlined C code -- this version is
        faster, dirtier and manipulates the numeric array in C.  This
        code was contributed by Eric Jones.  """
        g = grid
        nx, ny = g.u.shape
        dx2, dy2 = g.dx ** 2, g.dy ** 2
        dnr_inv = 0.5 / (dx2 + dy2)
        u = g.u
        
        code = """
               #line 151 "laplace.py"
               float tmp, err, diff;
               float *uc, *uu, *ud, *ul, *ur;
               err = 0.0;
               for (int i=1; i<nx-1; ++i) {
                   uc = u+i*ny+1;
                   ur = u+i*ny+2;     ul = u+i*ny;
                   ud = u+(i+1)*ny+1; uu = u+(i-1)*ny+1;
                   for (int j=1; j<ny-1; ++j) {
                       tmp = *uc;
                       *uc = ((*ul + *ur)*dy2 +
                              (*uu + *ud)*dx2)*dnr_inv;
                       diff = *uc - tmp;
                       err += diff*diff;
                       uc++;ur++;ul++;ud++;uu++;
                   }
               }
               return_val = sqrt(err);
               """
        # compiler keyword only needed on windows with MSVC installed
        err = weave.inline(code,
                           ['u', 'dx2', 'dy2', 'dnr_inv', 'nx', 'ny'],
                           compiler='gcc')
        return err
    
@available(flaplace is not None)
class fortran77(TimeSteper):
    'fortran77'
    
    @classmethod
    def time_step(cls, grid, dt=0.0):
        """fortran77
        Takes a time step using a simple fortran module that
        implements the loop in fortran90 arrays.  Use f2py to compile
        flaplace.f like so: f2py -c flaplace.f -m flaplace.  You need
        the latest f2py version for this to work.  This Fortran
        example was contributed by Pearu Peterson. """
        g = grid
        g.u, err = flaplace.timestep(g.u, g.dx, g.dy)
        return err
    
@available(flaplace90_arrays is not None)
class fortran90(TimeSteper):
    'fortran90'
    
    @classmethod
    def time_step(cls, grid, dt=0.0):
        """fortran90
        Takes a time step using a simple fortran module that
        implements the loop in fortran90 arrays.  Use
        f2py to compile flaplace_arrays.f90 like so: f2py -c
        flaplace_arrays.f90 -m flaplace90_arrays.  You need
        the latest f2py version for this to work.  This Fortran
        example was contributed by Ramon Crehuet. """
        g = grid
        g.u, err = flaplace90_arrays.timestep(g.u, g.dx, g.dy)
        return err
    
@available(flaplace95_forall is not None)
class fortran95(TimeSteper):
    'fortran95'
    
    @classmethod
    def time_step(cls, grid, dt=0.0):
        """fortran95
        Takes a time step using a simple fortran module that
        implements the loop in fortran95 forall construct.  Use
        f2py to compile flaplace_forall.f95 like so: f2py -c
        flaplace_forall.f95 -m flaplace95_forall.  You need
        the latest f2py version for this to work.  This Fortran
        example was contributed by Ramon Crehuet. """
        g = grid
        g.u, err = flaplace95_forall.timestep(g.u, g.dx, g.dy)
        return err
    
@available(pyx_lap is not None)
class pyrex(TimeSteper):
    'pyrex'
    
    @classmethod
    def time_step(cls, grid, dt=0.0):
        """pyrex
        Takes a time step using a function written in Pyrex.  Use
        the given setup.py to build the extension using the command
        python setup.py build_ext --inplace.  You will need Pyrex
        installed to run this."""        
        g = grid
        err = pyx_lap.pyrexTimeStep(g.u, g.dx, g.dy)
        return err
            
def solve(grid, timeStep, n_iter=0, eps=1.0e-16):        
    """Solves the equation given an error precision -- eps.  If
    n_iter=0 the solving is stopped only on the eps condition.  If
    n_iter is finite then solution stops in that many iterations
    or when the error is less than eps whichever is earlier.
    Returns the error if the loop breaks on the n_iter condition
    and returns the iterations if the loop breaks on the error
    condition."""        
    err = timeStep(grid)
    count = 1

    while True:
        if n_iter and count >= n_iter:
            return err
        err = timeStep(grid)
        count = count + 1

    return err


def BC(x, y):    
    """Used to set the boundary condition for the grid of points.
    Change this as you feel fit."""    
    return (x ** 2 - y ** 2)

def create_parser():
    parser = ArgumentParser(description=__doc__)
    
    parser.add_argument('-n', '--size', type=int, default=1000)
    parser.add_argument('-i', '--n_iter', type=int, default=100)
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-m', '--method', dest='methods', action='append', default=[])
    parser.add_argument('-e', '--exclude', action='append', default=[])
    parser.add_argument('-a', '--all', action='store_true')
    parser.add_argument('-o', '--output', type=FileType('w'))
    
    return parser

def main():
    
    parser = create_parser()
    
    args = parser.parse_args()
    
    available = {title:func for title, func in timestep_methods.items() if func.available}
    un_available = {title:func for title, func in timestep_methods.items() if not func.available}
    
    if args.list:
        print 
        print "Available Methods:"
        for title, func in available.items():
            print "    +", title
        print 
        print "Unavailable Methods:"
        for title, func in un_available.items():
            print "    +", title
        print 
        return
    
    if args.all:
        methods = set(available.keys())
    else:
        methods = set(args.methods)
        
    methods = sorted(methods - set(args.exclude))
        
    print >> sys.stderr, "args.methods", methods
    print >> args.output, "method, time"
    for method in methods:
        
        if method == 'slow':
            n_iter = 1
            scale = n_iter
        else:
            n_iter = args.n_iter
            scale = 1
             
        print >> sys.stderr, "method", method
        print >> sys.stderr, " + Doing %d iterations on a %dx%d grid" % (n_iter, args.size, args.size)
        
        cls = timestep_methods[method]
        grid = cls.create_grid(args.size, args.size)
        grid.setBCFunc(BC)
        
        try:
            t0 = time.time()
            err = solve(grid, cls.time_step, n_iter, eps=1.0e-16)
            
            print "err: ", err 
            cls.finish(grid)
            seconds0 = time.time() - t0
            if method == 'slow':
                print >> sys.stderr, " + Took", seconds0 * scale, "seconds (estimate)"
                print >> args.output, '%s, %r' % (method, seconds0 * scale)
            else:
                print >> sys.stderr, " + Took", seconds0, "seconds"
                print >> args.output, '%s, %r' % (method, seconds0)
        except Exception as err:
            print "%s: %s" % (type(err), err)
    return
     

if __name__ == "__main__":
    main()
    print "done!"
