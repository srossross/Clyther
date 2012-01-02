'''
Created on Sep 24, 2011

@author: sean
'''

from setuptools import setup, find_packages

import numpy
include_dirs = numpy.get_include()

setup(
    name='Clyther',
    version='0.2.1-beta',
    author='Enthought, Inc.',
    author_email='srossross@enthought.com',
    url='srossross.github.com/CLyther',
    classifiers=[c.strip() for c in """\
        Development Status :: 4 - Beta
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: Python
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.strip()) > 0],
    description='OpenCL Python integration',
    long_description=open('README.rst').read(),
    license='BSD',
    packages=find_packages(),
    platforms=["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    install_requires=['meta', 'opencl-for-python']
)

