============================================================
Getting Started
============================================================

easy_install 
--------------------

you can just run::
    
    sudo easy_install clyther

Prerequisites
--------------------

* `Meta <http://srossross.github.com/Meta>`_
* `OpenCL for Python <http://srossross.github.com/oclpb>`_

Download
--------------------

* `Stable version from PyPi <http://pypi.python.org/pypi/clyther>`_
* `The latest from GitHub <https://github.com/srossross/clyther/tags>`_

Build
--------

run::

    python setup.py build
    python setup.py install [ --prefix=$SOMEPATH ]

Test
--------

run::

    python -m unittest discover clyther/
