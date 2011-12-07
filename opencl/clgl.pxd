
from _cl cimport * 

cdef extern from "OpenCL/cl_gl_ext.h":
    enum gl_context_properties:
        CL_CONTEXT_PROPERTY_USE_CGL_SHAREGROUP_APPLE

cdef extern from "OpenGL/gl.h":
    void * CGLGetCurrentContext()
    void * CGLGetShareGroup(void *)
    
    ctypedef unsigned GLuint
    ctypedef int GLint
    ctypedef void GLvoid
    ctypedef size_t GLsizeiptr
    ctypedef size_t GLsizei
    
    enum cl_gl_error:
        CL_INVALID_GL_OBJECT
        
    enum cl_gl_object_type:
        CL_GL_OBJECT_BUFFER
        CL_GL_OBJECT_TEXTURE2D
        CL_GL_OBJECT_TEXTURE3D
        CL_GL_OBJECT_RENDERBUFFER
        
    ctypedef int GLenum
    
    cdef GLenum GL_ARRAY_BUFFER
    cdef GLenum GL_STATIC_DRAW
    cdef GLenum GL_NO_ERROR
    cdef GLenum GL_TEXTURE_2D
    cdef GLenum GL_TEXTURE_3D
    cdef GLenum GL_UNSIGNED_BYTE
    
    
    void glGenBuffers(size_t, GLuint *)
    void glBindBuffer(GLenum, GLuint)
    void glBufferData(GLenum, GLsizeiptr, GLvoid * , GLenum)
    
    GLenum glGetError()
     
    void glEnable(GLenum) 
    void glGenTextures(GLsizei, GLuint *)
    void glBindTexture(GLenum, GLuint)

    void glTexImage2D(GLenum, GLint, GLint, GLsizei, GLsizei, GLint, GLenum, GLenum, GLvoid *)
    void glTexImage3D(GLenum, GLint, GLint, GLsizei, GLsizei, GLsizei, GLint, GLenum, GLenum, GLvoid *)

    cdef GLenum GL_RGBA8, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8_REV, CL_RGBA, GL_BGRA, \
                GL_UNSIGNED_INT_8_8_8_8_REV, CL_BGRA, GL_RGBA16, GL_RGBA8I, \
                GL_RGBA8I_EXT, GL_RGBA16I, GL_RGBA16I_EXT, GL_RGBA32I, GL_RGBA32I_EXT, \
                GL_RGBA8UI, GL_RGBA8UI_EXT, GL_RGBA16UI, GL_RGBA16UI_EXT, GL_RGBA32UI, \
                GL_RGBA32UI_EXT, GL_RGBA16F, GL_RGBA16F_ARB, GL_RGBA32F, GL_RGBA32F_ARB


cdef extern from "OpenCL/cl_gl.h":
    
    cl_mem clCreateFromGLBuffer(cl_context, cl_mem_flags, unsigned, cl_int *)
    
    cl_mem clCreateFromGLTexture2D(cl_context, cl_mem_flags, GLenum, GLint, GLuint, cl_int *)
    cl_mem clCreateFromGLTexture3D(cl_context, cl_mem_flags, GLenum, GLint, GLuint, cl_int *)

    cl_int clGetGLObjectInfo(cl_mem memobj, cl_gl_object_type * gl_object_type, GLuint * gl_object_name)
    
    cl_int clEnqueueAcquireGLObjects(cl_command_queue, cl_uint, cl_mem * , cl_uint, cl_event * , cl_event *)
    cl_int clEnqueueReleaseGLObjects(cl_command_queue, cl_uint, cl_mem * , cl_uint, cl_event * , cl_event *)
    

   
