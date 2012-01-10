'''
Created on Sep 24, 2011

@author: sean
'''

from setuptools import setup, find_packages
from os.path import join
import numpy
include_dirs = numpy.get_include()

try:
    long_description = open('README.rst').read()
except IOError as err:
    long_description = str(err)

try:
    exec open(join('clyther', 'version.py')).read()
except IOError as err:
    __version__ = '???'


setup(
    name='Clyther',
    version=__version__,
    author='Enthought, Inc.',
    author_email='srossross@enthought.com',
    url='http://srossross.github.com/Clyther/',
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
    long_description=long_description,
    license='BSD',
    packages=find_packages(),
    platforms=["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
    install_requires=['meta', 'opencl-for-python']
)

