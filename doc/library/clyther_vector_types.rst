:mod:`clyther.vector_types` --- Expose OpenCL vector types to python
===================================================================================

.. module:: clyther.vector_types
   :synopsis: Expose OpenCL vector types to python
.. moduleauthor:: Sean Ross-Ross <srossross@geospin.ca>

.. versionadded:: 0.1-beta


Vector Components
------------------

.. class:: VectorBase( )
    
    .. attribute:: s0123456789ABCDEF
    
        The vector may access attributes s0 through sF.
    
    .. attribute:: xyzw

    .. attribute:: hi

        The upper half of the elements in the vector.

    .. attribute:: lo
        
        The lower half of the elements in the vector.
        
    .. attribute:: even
        
        The even elements of the vector.
        
    .. attribute:: odd
    
        The odd elements of the vector.
    
    

Vector Types
------------------

.. class:: uchar{2|4|8|16}( )
.. class:: uint{2|4|8|16}( )
.. class:: int{2|4|8|16}( )
.. class:: float{2|4|8|16}( )
    
    
Transpose Example
------------------

In this example argument ``m`` must be a float4 vector object
::

    import clyther
    from clyther.vector_types import float16,float4

    @clyther.task
    def transpose( m ):
        """
        transpose a 4x4 matrix
        """
    
        t = float16()
    
        x = float16( m[0], m[1], m[2], m[3] )
    
        t.even = x.lo
        t.odd = x.hi
        x.even = t.lo
        x.odd = t.hi
    
        #write back 
        m[0] = x.lo.lo 
        m[1] = x.lo.hi
        m[2] = x.hi.lo
        m[3] = x.hi.hi
    
.. seealso::
        
    The example in the directory ``examples/vector_transpose.py``
    
    