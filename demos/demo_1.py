'''
Created on Dec 15, 2011

@author: sean
'''

import opencl as cl
from clyther.array import CLArrayContext
#Always have to create a context.
ca = CLArrayContext()

#can print the current devices
print ca.devices

#Create an array
a = ca.arange(12)

print a

#map is the same as a memory map
with a.map() as arr:
    print arr

#can clice
b = a[1::2]

with b.map() as arr:
    print arr

#ufuncs
c = a + 1

with c.map() as arr:
    print arr
