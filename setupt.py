'''
Created on Sep 24, 2011

@author: sean
'''

from setuptools import setup, find_packages

setup(
    name = 'Clyther',
    version = '0.1',
    author = 'Enthought, Inc.',
    author_email = 'srossross@enthought.com',
    url = 'https://github.com/srossross/Magenta-Kangaroo',
    classifiers = [c.strip() for c in """\
        Development Status :: 5 - Production/Stable
        Intended Audience :: Developers
        Intended Audience :: Science/Research
        License :: OSI Approved :: BSD License
        Operating System :: MacOS
        Operating System :: Microsoft :: Windows
        Operating System :: OS Independent
        Operating System :: POSIX
        Operating System :: Unix
        Programming Language :: Python
        Programming Language :: OpenCL
        Topic :: Scientific/Engineering
        Topic :: Software Development
        Topic :: Software Development :: Libraries
        """.splitlines() if len(c.strip()) > 0],
    description = 'Open CL Python integration',
    long_description = open('README.rst').read(),
    license = 'BSD',
    packages = find_packages(),
    platforms = ["Windows", "Linux", "Mac OS-X", "Unix", "Solaris"],
)
