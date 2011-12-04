# IPython log file

import numpy as np
from opencl.copencl import Platform, get_platforms, Context, Device, Queue, Program, DeviceMemoryView, empty,empty_gl
from opencl.copencl import ContextProperties
from PySide.QtGui import *
from PySide.QtOpenGL import *

app = QApplication([])
qgl = QGLWidget()
qgl.makeCurrent()

props = ContextProperties()
props.gl_sharegroup = props.get_current_opengl_sharegroup()

ctx = Context(device_type=Device.DEFAULT, properties=props)

view = empty_gl(ctx, [10], ctype='ff')

view.shape

view[::2] = 1

print view
queue = Queue(ctx, ctx.devices[0])

with view.map(queue) as buffer:
    print np.asarray(buffer)

    
print "done"
