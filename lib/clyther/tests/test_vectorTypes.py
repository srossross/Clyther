'''
Created on Apr 12, 2010

@author: sean
'''
import unittest

import clyther


class Test(unittest.TestCase):

    
    def test_vector_init(self):
        "vector: Check type 'uint2' constructor"
        
        @clyther.task
        def construct( a ):
            a[0] = clyther.uint4( 4,3,2,1 )
            
            c = clyther.uint2(3,4)
            a[1] = clyther.uint4( clyther.uint2(1,2), c  )
            
            a[2] = clyther.uint4( 99 )
        
        a = clyther.DeviceBuffer( [3], elem_type=clyther.uint4 )
        
        #device
        construct( a ).wait( )
        
        dev_result = (clyther.uint4*3)()
        host_result = (clyther.uint4*3)()
        a.to_host(dev_result, block=True)
        
        #host
        
        clyther.emulate( construct, host_result )
        
        self.failUnlessEqual(dev_result[0], host_result[0] )

        
    def test_vector_even_odd(self):
        "vector: Check uint2.odd and uint2.even"
        
        @clyther.task
        def _dev_test( a ):
            b = clyther.uint4( 1,2,3,4 )
            a[0].even = b.odd
            a[0].odd = b.even
        
        a = clyther.DeviceBuffer( [1], elem_type=clyther.uint4 )
        _dev_test( a ).wait( )
        
        _first = [clyther.uint4()]
        clyther.emulate( _dev_test, _first )
        
        first = _first[0]
        second = a.item( )
        
        self.failUnlessEqual(first, second )

    def test_vector_hi_lo(self):
        "vector: Check uint2.hi and uint2.lo"
        
        @clyther.task
        def _dev_test( a ):
            b = clyther.uint4( 1,2,3,4 )
            a[0].lo = b.hi
            a[0].hi = b.lo
        
        a = clyther.DeviceBuffer( [1], elem_type=clyther.uint4 )
        _dev_test( a ).wait( )
        
        _first = [clyther.uint4()]
        clyther.emulate( _dev_test, _first )
        
        first = _first[0]
        second = a.item( )
        
        self.failUnlessEqual(first, second )

if __name__ == "__main__":
    
    clyther.init( 'gpu' )
    unittest.main()
    clyther.finish( )
