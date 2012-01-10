==============================
CLyther as a SEJITS Toolkit
==============================

The target audience for this page is familiar with either Copperhead or ASP.

SEJITS Python projects:
    * `Copperhead <http://code.google.com/p/copperhead/>`_
    * `ASP <https://github.com/shoaibkamil/asp/wiki>`_ A SEJITS Implementation for Python


How does CLyther fit in to the SEJITS ecosystem?
-------------------------------------------------

In this document I will break the a SEJITS project into three conceptual layers:

1. Front end: 
    * This is the side an end user will see. 
    * Ideally the user would require little to no knowledge outside of his or her comfort zone. 
      In this example I am targeting NumPy Users.
    * Hopefully we can take advantage of as much existing code as possible.   
    * The front end is the reason for SEJITS existence. We have to keep the Productivity Level Language (PLL) *Productive*

2. High level translation:
    * This layer defines complex translations from High level Python constructs to Mid-level constructs.
    * Little to no existing code will be written for this.
      Currently, writing these abstractions (map, reduce, list comprehensions) in Python are far too slow for high performance computing so they are not used.

3. Specialization Layer:
    * This layer targets domain experts in the specialization target language. This is the backbone of a SEJITS toolkit. 

Front End:
^^^^^^^^^^^

CLyther allows the user to define a context to drive the *selection* mechanizm of the SEJITS. 

This has the following advantages:

    * This answers the question *How does the SEJITS select the specialization algorithm?*
    
    * The data may now be created in the current context. 
        * This allows for efficient allocation 
        * No or optimized memory transfers when calling a specialized function.
        
    * The current SEJITS implementation work only on functional programming examples. 
      This solution allows equivalent or *mock* objects to be created in place of Python objects. 
      
      .. note:: This is true for Copperhead. Please correct me if this is not true for ASP. 

This example relies heavily on NumPy. The :class:`clyther.array.CLArrayContext` mimics the 
NumPy name-space but creates a memory buffer directly on the GPU::

    from clyther.array import *
    
    ca = CLArrayContext(device_type='gpu')
    
    a = ca.arange(1e5)
     
    a += 1
    
    jitable_function(ca, a, 1, 3)
    
This is particularly exciting because `NumPy UFuncs <http://docs.scipy.org/doc/numpy/reference/ufuncs.html>`_ are a low hanging fruit. 
We may be able to get an order of magnitude numpy performance while maintaining %100 percent backwards compatibility if we can specialize UFuncs at runtime.

High Level translation:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In copperhead::

    from copperhead import *
    import numpy as np
    
    @cu
    def double_array(array):
      return [a * 2 for a in array]
    
    arr = np.arange(100, dtype=np.float64)
    
    with places.gpu0:
      gpu = axpy(arr)


CLyther also provides High Level translation for element-wise operations::

    #Either
    
    @ca.unary_ufunc
    def double_array(element):
        return element * 2
    
    new_arr = double_array(arr)
    
    # === OR ===
    
    new_arr = ca.map(lambda x: x*2, arr)

Specialization Layer:
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ASP and Copperhead both use string templates to generate jit specializations. CLyther however defines a one to one mapping between Python and 
the target language. (So far only OpenCL is supported). In this way we can define specializations without strings in pure Python.  

From the source code of ASP we see that the ArrayDoubler requires a mako template `double_template.mako` which is not shown here::

    # really dumb example of using templates w/asp

    class ArrayDoubler(object):
        
        def __init__(self):
            self.pure_python = True
    
        def double_using_template(self, arr):
            import asp.codegen.templating.template as template
            mytemplate = template.Template(filename="templates/double_template.mako", disable_unicode=True)
            rendered = mytemplate.render(num_items=len(arr))
    
            import asp.jit.asp_module as asp_module
            mod = asp_module.ASPModule()
            # remember, must specify function name when using a string
            mod.add_function("double_in_c", rendered)
            return mod.double_in_c(arr)
    
        def double(self, arr):
            return map (lambda x: x*2, arr)



CLyther Specialization for OpenCL::

    class ArrayDoubler(object):
        
        def __init__(self):
            self.pure_python = True
    
        def double_using_template(self, arr):
            
            # Define an OpenCL kernel
            @cly.kernel 
            def my_kernel(arr, output):
                idx = clrt.get_global_id(0)
                output[idx] = arr[idx]
            
            output = ca.zeros_like(arr)
            
            my_kernel(ca, arr, output)
            
            return output
    
        def double(self, arr):
            return map (lambda x: x*2, arr)

    
Translation directly from the Python byte-code
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

CLyther uses the `Meta <http://srossross.github.com/Meta/html/index.html>`_ package to decompile Python byte-code in to a Python AST.
This means that a function can go thought any number of transformations before it is specialized. The most trivial examples being:
    1) Defining a function in the Python interpreter.  
    2) A lambda expression.

Example::
    
    half_source = 'def foo(a, b):'   
    second_half = '    return a+b'   
    
    exec half_source + second_half
    
    foo = ca.binary_ufunc(foo)
    
    
Conclusion
-------------------------------------------------

In developing CLyther I focused on developing the front and back ends of a SEJITS toolkit. ASP and Copperhead in particular have created an 
incredible mapping from high level Python abstractions to domain specific code.   

I think that a combination of all of these elements are needed to create a useful product.

Clyther focuses primaraly on the  
