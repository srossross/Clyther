This directory contains the sources for the Performance Python article
here:

 http://www.scipy.org/PerformancePython

Essentially, a simple Gauss-Seidel/Gauss-Jordan iterative scheme to
solve Laplace's equation is implemented in a variety of ways.  These
are compared for sheer speed.  Presently the script compares, pure
Python, pure Python + Psyco, Numeric, weave.blitz, weave.inline,
fortran (via f2py) and Pyrex.


Files:
^^^^^^

 laplace.py -- A script to compare the various options.

 setup.py --  Builds the Fortran and Pyrex modules.

 src/ -- Contains the Fortran and Pyrex sources.

 src/flaplace.f -- Fortran source that is wrapped with f2py.
 
 src/flaplace90_arrays.f90 -- Fortran90 version using array features. Wrapped with f2py.

 src/flaplace95_forall.f95 -- Fortran95 version using forall construct. Wrapped with f2py.

 src/pyx_lap.pyx -- Pyrex version.

 src/pyx_lap1.pyx -- Alternative Pyrex version contributed by Francesc
                     Alted that works with Numeric and Numarray and
                     presents a different way to access the array
                     data.  This is not compiled by default but is
                     there for reference.

 src/laplace.cxx -- Pure C++ version - just for kicks.  To compile it
                    do something like this:
                       g++ -O3 laplace.cxx -o lap


Requirements:
^^^^^^^^^^^^^

 Python, NumPy, SciPy (for weave), Pyrex and optionally Psyco.

Usage:
^^^^^^

 First run this:

  python setup.py build_ext --inplace

 Then simply run this:

  python laplace.py

 The C++ example in src/laplace.cxx can be run like so:

  $ ./lap 
  Enter nx n_iter eps --> 500 100 1e-16 [Return]
  [...]


Prabhu Ramachandran <prabhu_r at users dot sf dot net>
Fortran90 and 95 versions contributed by Ramon Crehuet 
<ramon.crehuet at iqac dot csic dot es>
