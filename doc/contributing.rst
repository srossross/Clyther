.. _contribute:

==============
Contributing
==============


What can you do to help?

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
    
    clamp = RuntimeFunction('clamp', # Name of the function 
                            lambda argtype, *args: argtype, # Return type. 
                            gentype(), sgentype(), sgentype(), # Argument types 
                            doc='Returns min(max(x, minval), maxval)',  # Docstrng
                            emulate=lambda x, minval, maxval : min(max(x, minval), maxval # Pure python function for emulation mode.
                            )
 
Once you get this working you can put it in the Python clyther.runtime module following the 
`Nice Git development Model <nvie.com/posts/a-successful-git-branching-model/>`_ and send me a pull request. 
Or send me a patch file via email srossross@enthought.com.


If the function has an existing python equivalent. i.e. `acos` then you could specify the `builtin` argument::

    acos = RuntimeFunction('acos', # Name of the function 
                            lambda argtype: argtype, # Return type. 
                            gentype() # Argument types 
                            doc='Returns acos(value)',  # Docstring
                            builtin=math.acos # Alternate function
                            )
                            
This will allow :func:`clyther.runtime.acos` and :func:`math.acos` to be used interchangeably. 

.. seealso::

    * :class:`clyther.rttt.RuntimeFunction`
    * `Git development Model <nvie.com/posts/a-successful-git-branching-model/>`_
    
Errors
^^^^^^^^^^^^^^^^^^^^

My goal is to make OpenCL as easy and friendly to use as possible. 
If you get an error that is not intuitive please post an issue on the `GitHub issue tracker <https://github.com/srossross/clyther/issues>`_. 

Transformation Pipeline
^^^^^^^^^^^^^^^^^^^^^^^^^^

CLyther transforms a Python ast into an OpecnCL ast and then compiles it using `OpenCL for Python <https://github.com/srossross/oclpb>`_.
The ast transformation pipline can be found at :mod:`clyther.pipeline`.  


CLyther.array
^^^^^^^^^^^^^^^^^^^^^^^^^^

I would like to get a chunk of the core numpy functionality reproduced. 


Documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^

I have just whipped up the documentation and I am notorious for my spelling typos. Please let me know! 
All documentation and other input is most welcome.    



