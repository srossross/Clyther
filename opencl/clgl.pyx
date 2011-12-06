import struct
from opencl.errors import OpenCLException
import opencl.errors


from _cl cimport *
from clgl cimport *

from libc.stdlib cimport malloc, free 
from cpython cimport PyObject, Py_DECREF, Py_INCREF, PyBuffer_IsContiguous, PyBuffer_FillContiguousStrides
from cpython cimport Py_buffer, PyBUF_SIMPLE, PyBUF_STRIDES, PyBUF_ND, PyBUF_FORMAT, PyBUF_INDIRECT, PyBUF_WRITABLE

from opencl.cl_mem cimport CyView_Create,CyMemoryObject_Check,CyMemoryObject_GetID
from opencl.context cimport ContextFromPyContext
from opencl.queue cimport CyQueue_GetID, CyQueue_Check, _make_wait_list
from opencl.copencl cimport PyEvent_New

opencl.errors.all_opencl_errors.update(
    {
     CL_INVALID_GL_OBJECT : 'CL_INVALID_GL_OBJECT',
     })

opencl.errors.OpenCLErrorStrings.update({
    CL_INVALID_GL_OBJECT : "There is no GL object associated with memobj",
    })


def get_current_opengl_context():
    return < size_t > CGLGetCurrentContext()

def get_current_opengl_sharegroup():
    return < size_t > CGLGetShareGroup(< void *> CGLGetCurrentContext())

def set_opengl_properties(context_properties):
    context_properties.set_property("gl_sharegroup", <size_t>CL_CONTEXT_PROPERTY_USE_CGL_SHAREGROUP_APPLE,
                                <size_t> get_current_opengl_sharegroup())

def is_gl_object(memobject):
    if not CyMemoryObject_Check(memobject):
        raise TypeError("argument must be of type 'cl.MemoryObject'")
    
    cdef cl_int err_code = 0
    cdef cl_mem memobj = CyMemoryObject_GetID(memobject)
    err_code = clGetGLObjectInfo(memobj, NULL, NULL)
    
    if err_code == CL_INVALID_GL_OBJECT:
        return False
    elif err_code != CL_SUCCESS:
        raise OpenCLException(err_code)
    
    return True
    
def get_gl_name(memobject):
    
    if not CyMemoryObject_Check(memobject):
        raise TypeError("argument must be of type 'cl.MemoryObject'")
    
    cdef GLuint gl_object_name = 0
    cdef cl_int err_code = 0
    cdef cl_mem memobj = CyMemoryObject_GetID(memobject)
    err_code = clGetGLObjectInfo(memobj, NULL, &gl_object_name)
    
    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)

    return gl_object_name
    
def empty_gl(context, shape, ctype='B', gl_buffer=None):
    
    cdef cl_context ctx = ContextFromPyContext(context)

    cdef cl_mem_flags flags = CL_MEM_READ_WRITE
    
    cdef Py_buffer *buffer = <Py_buffer *>malloc(sizeof(Py_buffer))
    cdef cl_int err_code
    
    if isinstance(ctype, str):
        buffer.format = ctype
    else:
        buffer.format = ctype._type_

    buffer.itemsize = struct.calcsize(buffer.format)
    
    cdef size_t size = buffer.itemsize
    
    for i in shape:
        size *= i
       
    cdef GLuint vbo = 0
    cdef GLsizeiptr nbytes = 0
    
    if gl_buffer is None:
        glGenBuffers(1, & vbo)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        
        nbytes = buffer.itemsize
        
        for i in shape:
            nbytes *= i
                    
        glBufferData(GL_ARRAY_BUFFER, nbytes, NULL, GL_STATIC_DRAW)
        
        if glGetError() != GL_NO_ERROR:
            raise Exception("OpenGL error")
    else:
        vbo = <GLuint> gl_buffer
    
    cdef cl_mem buffer_id = clCreateFromGLBuffer(ctx, flags, vbo, & err_code)
    
    if gl_buffer is None:
        glBindBuffer(GL_ARRAY_BUFFER, 0)
    
    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)
    
    buffer.readonly = 0
    buffer.ndim = len(shape)
    
    buffer.shape = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer.strides = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    buffer.suboffsets = < Py_ssize_t *> malloc(sizeof(Py_ssize_t) * buffer.ndim)
    
    for i in range(buffer.ndim):
        buffer.shape[i] = shape[i]
        buffer.suboffsets[i] = 0
    
    PyBuffer_FillContiguousStrides(buffer.ndim, buffer.shape, buffer.strides, buffer.itemsize, 'C')
    
    return CyView_Create(buffer_id, buffer, 0)


class acquire(object):
    def __init__(self, queue, *mem_objects, wait_on=()):
        self.queue = queue
        self.mem_objects = mem_objects
        self.wait_on = wait_on
        
    def __enter__(self):
        enqueue_acquire_gl_objects(self.queue, self.mem_objects, wait_on=self.wait_on)
        
    def __exit__(self, *args):
        enqueue_release_gl_objects(self.queue, self.mem_objects)
        

def enqueue_acquire_gl_objects(queue, *mem_objects, wait_on=()):
    
    if not CyQueue_Check(queue):
        raise TypeError("argument 'queue' is required to be a valid cl.Queue object")
    
    cdef cl_int err_code
    
    cdef cl_event * event_wait_list
    cdef cl_uint num_events_in_wait_list = _make_wait_list(wait_on, & event_wait_list)
    
    if event_wait_list == < cl_event *> 1:
        raise Exception("One of the items in argument 'wait_on' is not a valid event")

    if len(mem_objects) == 1:
        if isinstance(mem_objects[0], (list,tuple)):
            mem_objects = mem_objects[0]
            
    cdef cl_uint num_objects =0
    cdef cl_mem *mem_object_ids = NULL
    cdef cl_event event_id
    cdef cl_command_queue command_queue = CyQueue_GetID(queue)
    cdef int i
    
    num_objects = len(mem_objects)
    
    if num_objects ==0:
        return None 
    
    mem_object_ids = <cl_mem *> malloc(sizeof(cl_mem) * num_objects)
    for i in range(num_objects):
        if not CyMemoryObject_Check(mem_objects[i]):
            free(mem_object_ids)
            raise TypeError("argument mem_objects got an invalid MemoryObject (got %r)" %type(mem_objects[i]))
        
        mem_object_ids[i] = CyMemoryObject_GetID(mem_objects[i])
        
    err_code = clEnqueueAcquireGLObjects(command_queue, num_objects, mem_object_ids,
                                         num_events_in_wait_list, event_wait_list, &event_id)

    free(mem_object_ids)
    
    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)

    return PyEvent_New(event_id)

def enqueue_release_gl_objects(queue, *mem_objects, wait_on=()):
    
    if not CyQueue_Check(queue):
        raise TypeError("argument 'queue' is required to be a valid cl.Queue object")
    
    cdef cl_int err_code
    
    cdef cl_event * event_wait_list
    cdef cl_uint num_events_in_wait_list = _make_wait_list(wait_on, & event_wait_list)
    
    if event_wait_list == < cl_event *> 1:
        raise Exception("One of the items in argument 'wait_on' is not a valid event")

    if len(mem_objects) == 1:
        if isinstance(mem_objects[0], (list,tuple)):
            mem_objects = mem_objects[0]
            
    cdef cl_uint num_objects =0
    cdef cl_mem *mem_object_ids = NULL
    cdef cl_event event_id
    cdef cl_command_queue command_queue = CyQueue_GetID(queue)
    cdef int i
    
    num_objects = len(mem_objects)
    
    if num_objects ==0:
        return None 
    
    mem_object_ids = <cl_mem *> malloc(sizeof(cl_mem) * num_objects)
    for i in range(num_objects):
        if not CyMemoryObject_Check(mem_objects[i]):
            free(mem_object_ids)
            raise TypeError("argument mem_objects got an invalid MemoryObject (got %r)" %type(mem_objects[i]))
        
        mem_object_ids[i] = CyMemoryObject_GetID(mem_objects[i])
        
    err_code = clEnqueueReleaseGLObjects(command_queue, num_objects, mem_object_ids,
                                         num_events_in_wait_list, event_wait_list, &event_id)

    free(mem_object_ids)
    
    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)

    return PyEvent_New(event_id)

