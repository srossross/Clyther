'''
Created on Dec 24, 2011

@author: sean
'''
import clyther as cly
from clyther.array import CLArrayContext
import opencl as cl
import unittest
import math
import os
import numpy as np


ca = None

def setUpModule():
    global ca
    
    
    DEVICE_TYPE_ATTR = os.environ.get('DEVICE_TYPE', 'DEFAULT')
    DEVICE_TYPE = getattr(cl.Device, DEVICE_TYPE_ATTR)
    
    ca = CLArrayContext(device_type=DEVICE_TYPE)
    
    print ca.devices

class Test(unittest.TestCase):

    def test_cos(self):
        
        @cly.task
        def do_sin(ret, value):
            ret[0] = math.sin(value)
         
        cy = ca.empty([1], 'f')
        nu = np.empty([1], 'f')
         
        do_sin(cy.queue, cy, math.pi / 2)
        do_sin.emulate(cy.queue, nu, math.pi / 2)
        
        with cy.map() as arr:
            self.assertTrue(np.allclose(arr, nu))

    def test_sin(self):
        
        @cly.task
        def do_sin(ret, value):
            ret[0] = math.sin(value)
         
        cy = ca.empty([1], 'f')
        nu = np.empty([1], 'f')
         
        do_sin(cy.queue, cy, math.pi / 2)
        do_sin.emulate(cy.queue, nu, math.pi / 2)
        
        with cy.map() as arr:
            self.assertTrue(np.allclose(arr, nu))



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.test_sim']
    unittest.main()
