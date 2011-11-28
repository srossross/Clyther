************************************
  Getting Started
************************************

.. warning::  
    
    Clyther is currently under development.  This is an **alpha** release of CLyther. Please report all errors you encounter. 
 	
 	Thanks 

 
 


Prerequisites
================

	*OpenCL*:
		of course
		
	*Numpy*:
		The clyther library does not require numpy but some of the examples and tests do.


Getting CLyther
================

Official source and binary releases
----------------------------------------

Official releases are on `SourceForge download site for clyther <https://sourceforge.net/projects/clyther/files>`_. 

clyther is currently in its alpha release and it is recommended to `download clyther-alpha-1.0 <https://sourceforge.net/projects/clyther/alpha/clyther-alpha-1.0.tar.gz/download>`_.

SVN repository access 
----------------------------------------

Dev::

	svn co https://clyther.svn.sourceforge.net/svnroot/clyther/TRUNK clyther
	
	
Alpha::

	svn co https://clyther.svn.sourceforge.net/svnroot/clyther/branches/alpha clyther 


Build/Install
================

To build and instal CLyther run::
	
	python setup.py build
	python setup.py install


Running the tests
==================

::
    
    python setup.py test

Running the examples
===============================================================================

Once you have built or installed clyther and correctly set your `PYTHONPATH <http://docs.python.org/using/cmdline.html#envvar-PYTHONPATH>`_ variable
you may run any script in the example directory::

   $python example/reduce_example.py

The result should be the same as the numpy results::

	starting array [ ... random ... ]
	
	            numpy |     OpenCL  
	------------------+-------------
	sum         46.20 =      46.20
	prod     69117.67 =   69117.69
	max          2.00 =       2.00


Feedback
===============================================================================

Please give us your feedback !!!

* `Mailing list <https://lists.sourceforge.net/lists/listinfo/clyther-devel>`_
* `Bug Tracking <http://sourceforge.net/tracker/?group_id=306335&atid=1290683>`_
* `Feature Requests <http://sourceforge.net/tracker/?group_id=306335&atid=1290686>`_
	
	


