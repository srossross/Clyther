import struct
from opencl.errors import OpenCLException
import opencl as cl
import opencl.errors
from opencl.type_formats import type_format, size_from_format

from _cl cimport * 
from clgl cimport * 

from libc.stdlib cimport malloc, free
from libc.string cimport strcpy 
 
from cpython cimport PyObject, Py_DECREF, Py_INCREF, PyBuffer_IsContiguous, PyBuffer_FillContiguousStrides
from cpython cimport Py_buffer, PyBUF_SIMPLE, PyBUF_STRIDES, PyBUF_ND, PyBUF_FORMAT, PyBUF_INDIRECT, PyBUF_WRITABLE

from opencl.cl_mem cimport CyView_Create, CyMemoryObject_Check, CyMemoryObject_GetID, CyImageFormat_New, CyImage_New
from opencl.context cimport CyContext_GetID, CyContext_Check
from opencl.queue cimport CyQueue_GetID, CyQueue_Check, _make_wait_list
from opencl.copencl cimport PyEvent_New

opencl.errors.all_opencl_errors.update(
    {
     CL_INVALID_GL_OBJECT : 'CL_INVALID_GL_OBJECT',
     })

opencl.errors.OpenCLErrorStrings.update({
    CL_INVALID_GL_OBJECT : "There is no GL object associated with memobj",
    })

IMAGE_FORMAT_MAP = (
                    

    (GL_RGBA8, (CL_RGBA, CL_UNORM_INT8)),
    (GL_RGBA8, (CL_BGRA, CL_UNORM_INT8)),

    (GL_RGBA, (CL_RGBA, CL_UNORM_INT8)),
    
    (GL_BGRA, (CL_RGBA, CL_UNORM_INT8)),
    (GL_UNSIGNED_INT_8_8_8_8_REV, (CL_RGBA, CL_UNORM_INT8)),

    (GL_RGBA16 , (CL_RGBA, CL_UNORM_INT16)),

#    (GL_RGBA8I, (CL_RGBA, CL_SIGNED_INT8)),
    (GL_RGBA8I_EXT, (CL_RGBA, CL_SIGNED_INT8)),

#    (GL_RGBA16I, (CL_RGBA, CL_SIGNED_INT16)),
    (GL_RGBA16I_EXT, (CL_RGBA, CL_SIGNED_INT16)),

#    (GL_RGBA32I, (CL_RGBA, CL_SIGNED_INT32)),
    (GL_RGBA32I_EXT, (CL_RGBA, CL_SIGNED_INT32)),

#    (GL_RGBA8UI, (CL_RGBA, CL_UNSIGNED_INT8)),
    (GL_RGBA8UI_EXT, (CL_RGBA, CL_UNSIGNED_INT8)),

#    (GL_RGBA16UI, (CL_RGBA, CL_UNSIGNED_INT16)),
    (GL_RGBA16UI_EXT, (CL_RGBA, CL_UNSIGNED_INT16)),

#    (GL_RGBA32UI, (CL_RGBA, CL_UNSIGNED_INT32)),
    (GL_RGBA32UI_EXT, (CL_RGBA, CL_UNSIGNED_INT32)),

#    (GL_RGBA16F, (CL_RGBA, CL_HALF_FLOAT)),
    (GL_RGBA16F_ARB, (CL_RGBA, CL_HALF_FLOAT)),

#    (GL_RGBA32F, (CL_RGBA, CL_FLOAT)),
    (GL_RGBA32F_ARB, (CL_RGBA, CL_FLOAT)),

    )


def get_gl_image_format(image_format):
    match = (image_format.channel_order, image_format.channel_data_type)
    
    for gl_format, cl_format in IMAGE_FORMAT_MAP:
        if cl_format == match:
            return gl_format
        
    raise Exception("opengl does not support this image %r" % (image_format)) 

def get_cl_image_format(match):
    
    cdef cl_image_format image_format
    for gl_format, (channel_order, channel_data_type) in IMAGE_FORMAT_MAP:
        if gl_format == match:
            image_format.image_channel_order = channel_order
            image_format.image_channel_data_type = channel_data_type
            
            return CyImageFormat_New(image_format)
        
    raise Exception("opencl does not support opeGL format %r" % (gl_format))

    
def get_current_opengl_context():
    return < size_t > CGLGetCurrentContext()

def get_current_opengl_sharegroup():
    return < size_t > CGLGetShareGroup(< void *> CGLGetCurrentContext())

def set_opengl_properties(context_properties):
    context_properties.set_property("gl_sharegroup", < size_t > CL_CONTEXT_PROPERTY_USE_CGL_SHAREGROUP_APPLE,
                                < size_t > get_current_opengl_sharegroup())

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
    err_code = clGetGLObjectInfo(memobj, NULL, & gl_object_name)
    
    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)

    return gl_object_name
    
def empty_gl_image(context, shape, image_format):

    if len(shape) not in [2, 3]:
        raise TypeError("image must be 2 or 3 dimentional (got %i)" % (len(shape),))
        
    if not CyContext_Check(context):
        raise TypeError("argument context must be an opencl.Context object")
    
    cdef cl_context ctx = CyContext_GetID(context)

    cdef cl_mem_flags flags = CL_MEM_READ_WRITE

    cdef Py_buffer * buffer = < Py_buffer *> malloc(sizeof(Py_buffer))
    cdef cl_int err_code
    
    cdef GLint miplevel = 0
    cdef GLint ntextures = 0
    cdef GLuint texture
    cdef cl_int width = shape[0]
    cdef cl_int height = shape[1]
    cdef cl_int depth = 1
    cdef GLenum format_e = GL_RGBA
    cdef GLenum type_e = GL_UNSIGNED_BYTE
    cdef cl_mem image
    
    if len(shape) == 2:
        glEnable(GL_TEXTURE_2D)
        glGenTextures(1, & texture) 
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, 4, width, height, 0, format_e, type_e, NULL)
        glBindTexture(GL_TEXTURE_2D, 0)
        
        image = clCreateFromGLTexture2D(ctx, flags, GL_TEXTURE_2D, miplevel, texture, & err_code)
        
    else : # len(shape) == 3
        depth = shape[2]
        glEnable(GL_TEXTURE_3D)
        glGenTextures(1, & texture) 
        glBindTexture(GL_TEXTURE_3D, texture)
        glTexImage3D(GL_TEXTURE_3D, 0, 4, width, height, depth, 0, format_e, type_e, NULL)
        glBindTexture(GL_TEXTURE_3D, 0)
        
        image = clCreateFromGLTexture3D(ctx, flags, GL_TEXTURE_3D, miplevel, texture, & err_code)
        
    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)

    cdef gl_err = glGetError()
    if gl_err != GL_NO_ERROR:
        raise Exception((gl_err, "OpenGL error"))

    return CyImage_New(image)
    
def empty_gl(context, shape, ctype='B', gl_buffer=None):
    
    if not CyContext_Check(context):
        raise TypeError("argument context must be an opencl.Context object")
    
    cdef cl_context ctx = CyContext_GetID(context)

    cdef cl_mem_flags flags = CL_MEM_READ_WRITE
    
    cdef Py_buffer * buffer = < Py_buffer *> malloc(sizeof(Py_buffer))
    cdef cl_int err_code
    
    if isinstance(ctype, str):
        format = ctype
    else:
        format = type_format(ctype)

    buffer.format = < char *> malloc(len(format) + 1)
    cdef char * tmp = < char *> format
    strcpy(buffer.format, tmp)

    buffer.itemsize = size_from_format(buffer.format)
    
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
        vbo = < GLuint > gl_buffer
    
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
        enqueue_acquire_gl_objects(self.queue, *self.mem_objects, wait_on=self.wait_on)
        
    def __exit__(self, *args):
        enqueue_release_gl_objects(self.queue, *self.mem_objects)
        

def enqueue_acquire_gl_objects(queue, *mem_objects, wait_on=()):
    
    if not CyQueue_Check(queue):
        raise TypeError("argument 'queue' is required to be a valid cl.Queue object")
    
    cdef cl_int err_code
    
    cdef cl_event * event_wait_list
    cdef cl_uint num_events_in_wait_list = _make_wait_list(wait_on, & event_wait_list)
    
    if event_wait_list == < cl_event *> 1:
        raise Exception("One of the items in argument 'wait_on' is not a valid event")

    print "mem_objects", mem_objects
    if len(mem_objects) == 1:
        if isinstance(mem_objects[0], (list, tuple)):
            mem_objects = mem_objects[0]
            
    cdef cl_uint num_objects = 0
    cdef cl_mem * mem_object_ids = NULL
    cdef cl_event event_id
    cdef cl_command_queue command_queue = CyQueue_GetID(queue)
    cdef int i
    
    num_objects = len(mem_objects)
    
    if num_objects == 0:
        return None 
    
    mem_object_ids = < cl_mem *> malloc(sizeof(cl_mem) * num_objects)
    for i in range(num_objects):
        if not CyMemoryObject_Check(mem_objects[i]):
            free(mem_object_ids)
            raise TypeError("argument mem_objects got an invalid MemoryObject (got %r)" % type(mem_objects[i]))
        
        mem_object_ids[i] = CyMemoryObject_GetID(mem_objects[i])
        
    err_code = clEnqueueAcquireGLObjects(command_queue, num_objects, mem_object_ids,
                                         num_events_in_wait_list, event_wait_list, & event_id)

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
        if isinstance(mem_objects[0], (list, tuple)):
            mem_objects = mem_objects[0]
            
    cdef cl_uint num_objects = 0
    cdef cl_mem * mem_object_ids = NULL
    cdef cl_event event_id
    cdef cl_command_queue command_queue = CyQueue_GetID(queue)
    cdef int i
    
    num_objects = len(mem_objects)
    
    if num_objects == 0:
        return None 
    
    mem_object_ids = < cl_mem *> malloc(sizeof(cl_mem) * num_objects)
    for i in range(num_objects):
        if not CyMemoryObject_Check(mem_objects[i]):
            free(mem_object_ids)
            raise TypeError("argument mem_objects got an invalid MemoryObject (got %r)" % type(mem_objects[i]))
        
        mem_object_ids[i] = CyMemoryObject_GetID(mem_objects[i])
        
    err_code = clEnqueueReleaseGLObjects(command_queue, num_objects, mem_object_ids,
                                         num_events_in_wait_list, event_wait_list, & event_id)

    free(mem_object_ids)
    
    if err_code != CL_SUCCESS:
        raise OpenCLException(err_code)

    return PyEvent_New(event_id)



def context(props=None):
    if props is None:
        props = cl.ContextProperties()
        
    set_opengl_properties(props)
    
    return cl.Context(device_type=cl.Device.DEFAULT, properties=props)
    
    