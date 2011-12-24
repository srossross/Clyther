.. Clyther documentation master file, created by
   sphinx-quickstart on Sat Sep 24 21:31:29 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Clyther's documentation!
===================================



Links:
+++++++++++

* `Homepage <http://srossross.github.com/clyther/develop/>`_
* `Issue Tracker <https://github.com/srossross/clyther/issues/>`_

* `Development documentation <http://srossross.github.com/clyther/develop/>`_
* `PyPi <http://pypi.python.org/pypi/clyther/>`_
* `Github <https://github.com/srossross/clyther/>`_
* `OpenCL 1.1 spec <http://www.khronos.org/registry/cl/specs/opencl-1.0.29.pdf>`_

* Also please check out `OpenCL for Python <http://srossross.github.com/oclpb>`_ 

Contributing
++++++++++++++++

* Author Email: srossross@enthought.com
* Enthought Email: info@enthought.com
* `Git development Model <nvie.com/posts/a-successful-git-branching-model/>`_

OpenCL built-ins
^^^^^^^^^^^^^^^^^^^^

I have intentionally put off filling out all of the OpenCL built-in functions. 


If you see an error like::
    
      File "/Users/sean/indigo_workspace/Clyther/clyther/cly_kernel.py", line 249, in translate
        eval(redirect_error_to_function) #use the @cly.developer function decorator to turn this off and see stack trace ...
      File "examples/tst.py", line 16, in <module>
        a[0] = clrt.clamp(x, 0, 1)
    AttributeError: 'module' object has no attribute 'clamp'

Then I have not yet added this function definition to the CLyther runtime module. Fortunately this is easy for you!

To add this to CLyther you can define clamp like so::

    import opencl as cl
    from clyther.rttt import RuntimeFunction, RuntimeType, gentype, sgentype, ugentype
    
    clamp = RuntimeFunction('clamp', lambda argtype, *args: 
                            argtype, 
                            gentype(), sgentype(), sgentype(), 
                            doc='Returns min(max(x, minval), maxval)')
 
Once you get this working you can put it in the python clyther.runtime module following the 
`Nice Git development Model <nvie.com/posts/a-successful-git-branching-model/>`_ and send me a pull request. 
Or send me a patch file via email srossross@enthought.com.

.. seealso::

    * :class:`clyther.rttt.RuntimeFunction`
    * `Git development Model <nvie.com/posts/a-successful-git-branching-model/>`_

Python built-ins
^^^^^^^^^^^^^^^^^

Contents:
++++++++++++++++

.. toctree::
   :maxdepth: 2
   
   getting_started
   performance_python
   for_numpy_users
   api
   
   
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

