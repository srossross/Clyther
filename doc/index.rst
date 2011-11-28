.. _index:

###############################
  CLyther dev documentation
###############################
     
.. note:: 

	The Beta version has been released. Please `Download <https://sourceforge.net/projects/clyther/files/beta/clyther-0.1-beta.tar.gz/download>`_. 
	and try the Beta version of CLyther. Or see the install instructions below.
	 
    Please tell us what you think. 
    You can email me directly `srossross@geospin.ca <mailto:srossross@geospin.ca>`_ or subscribe to the 
    developers mailing list `clyther-devel <mailto:clyther-devel-request@lists.sourceforge.net?subject=subscribe>`_.
    
    
    We are excited to release this product and we would like your help and feedback. 
    Please contact me if you would like to help develop CLyther.
    
    You may also post a comment to our `Forum <https://sourceforge.net/projects/clyther/forums/forum/1096292/topic/3562356/>`_.


CLyther is a python tool similar to `Cython <www.cython.org>`_.  CLyther is a python language extension that makes writing OpenCL code as easy as Python itself. CLyther currently only supports a subset of the Python language definition but adds many new features to OpenCL. CLyther was inspired by `PyCUDA <http://mathema.tician.de/software/pycuda>`_ and PyCUDA's views on  `Metaprogramming <http://en.wikipedia.org/wiki/Metaprogramming>`_.

CLyther exposes both the OpenCL C library as well as the OpenCL language to python.


Features
=========

Current Beta
--------------

Clyther allows:
 
 * OpenCL interface similar to PyOpenCL
 * Dynamic compilation at runtime
 * Fast prototyping of OpenCL code.
 * Create OpenCL code using the Python language definition.
 * Passing functions as arguments to kernel functions.
 * Python emulation mode of OpenCL code.
 * Device memory management
 

Next Release
-------------

 * Strong OOP programming in OpenCL code.
 * Create and define objects in Python to pass to kernel functions. 
 * Support for more python built-in functions and types 
 * Fancy indexing of arrays



Goals
=========

My objective with CLyther is to create an **extensible** library of **reusable** OpenCL functions.
These functions will be easy to prototype but also allow for optimization and exporting to 
static OpenCL code.

I think that adding an OOP aspect to OpenCL will allow more creativity and open new possibilities for OpenCL. 

Simple table:

=====  =====  ====== 
   Inputs     Output 
------------  ------ 
  A      B    A or B 
=====  =====  ====== 
False  False  False 
True   False  True 
False  True   True 
True   True   True 
=====  =====  ======


Table of contents
==================


.. toctree::
    
    install.rst
    tutorial/index.rst
    library/index.rst
    capi.rst
    copyright.rst
    license.rst


