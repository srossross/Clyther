
*******************************************************************************
*                                CLyther									  *  
*******************************************************************************

===============================================================================
 ALPHA Warning !!!
===============================================================================

 This is an alpha release of CLyther. Please report all errors you encounter. 
 Thanks 
 
===============================================================================
 Prerequisites 
===============================================================================
	
	OpenCL: of course
	Numpy: The clyther library does not require numpy but some of the
		   examples and tests do.
	

===============================================================================
 BUILD/INSALL
===============================================================================
	
	run:
	  python setup.py build
	 or
	  python setup.py install
	  
	  
===============================================================================
 EXAMPLE
===============================================================================

Once you have built or installed clyther and correctly set your PYTHONPATH variable
(see: http://docs.python.org/using/cmdline.html#envvar-PYTHONPATH )
	 
you may run any script in the example directory:

eg.
   $python example/reduce_example.py

The result should be an array of sixteen three's

	starting array [ ... ]
	
	            numpy |     OpenCL  
	------------------+-------------
	sum         46.20 =      46.20
	prod     69117.67 =   69117.69
	max          2.00 =       2.00

===============================================================================
 FEEDBACK
===============================================================================

Please give us your feedback !!!

Mailing list:     https://lists.sourceforge.net/lists/listinfo/clyther-devel	
Bug Tracking:     http://sourceforge.net/tracker/?group_id=306335&atid=1290683
Feature Requests: http://sourceforge.net/tracker/?group_id=306335&atid=1290686

