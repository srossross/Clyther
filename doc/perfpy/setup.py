from distutils.core import setup, Extension
from Cython.Distutils import build_ext
import os
import numpy

os.system('f2py -c src/flaplace.f -m flaplace')
os.system('f2py -c src/flaplace90_arrays.f90 -m flaplace90_arrays')
os.system('f2py -c src/flaplace95_forall.f95 -m flaplace95_forall')

setup(
    name = 'Laplace',
    ext_modules=[ Extension("pyx_lap",
                            ["src/pyx_lap.pyx"],
                            include_dirs = [numpy.get_include()]) ],
    cmdclass = {'build_ext': build_ext}
    )
