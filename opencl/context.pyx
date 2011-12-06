from opencl.errors import OpenCLException

from _cl cimport *
from opencl.copencl cimport clPlatformFromPyPlatform, clPlatformAs_PyPlatform
from opencl.copencl cimport DeviceIDFromPyDevice, DeviceIDAsPyDevice
from libc.stdlib cimport malloc, free 

cdef class ContextProperties:

    cdef cl_platform_id platform_id
    cdef size_t _gl_context
    cdef size_t _gl_sharegroup
    
    def __cinit__(self):
        self.platform_id = NULL
        self.gl_context = 0
        self._gl_sharegroup = 0
        
    property platform:
        def __get__(self):
            if self.platform_id != NULL:
                return clPlatformAs_PyPlatform(self.platform_id)
            else:
                return None

        def __set__(self, value):
            self.platform_id = clPlatformFromPyPlatform(value)

    property gl_context:
        def __get__(self):
            return self._gl_context

        def __set__(self, value):
            self._gl_context = value
            
    property gl_sharegroup:
        def __get__(self):
            return self._gl_sharegroup

        def __set__(self, value):
            self._gl_sharegroup = value
    
    @classmethod
    def get_current_opengl_context(cls):
        return < size_t > CGLGetCurrentContext()

    @classmethod
    def get_current_opengl_sharegroup(cls):
        return < size_t > CGLGetShareGroup(< void *> CGLGetCurrentContext())
        
    def as_dict(self):
        nprops = 0
        
        if self.platform_id != NULL:
            nprops += 1
        if self._gl_context != 0:
            nprops += 1
        if self._gl_context != 0:
            nprops += 1
            
        props = {}
           
        if self.platform_id != NULL:
             props[ < size_t > CL_CONTEXT_PLATFORM] = < size_t > self.platform_id
        if self._gl_sharegroup != 0:
             props[ < size_t > CL_CONTEXT_PROPERTY_USE_CGL_SHAREGROUP_APPLE] = < size_t > self._gl_sharegroup
        
        props[nprops * 2] = None
        
        return props
    
        
    cdef cl_context_properties * context_properties(self):
        
        nprops = 0
        cdef cl_context_properties * props = NULL
        
        if self.platform_id != NULL:
            nprops += 1
        if self._gl_context != 0:
            nprops += 1
        if self._gl_sharegroup != 0:
            nprops += 1
            
        if nprops > 0:
            props = < cl_context_properties *> malloc(sizeof(cl_context_properties) * (1 + 2 * nprops))
           
        cdef count = 0
        if self.platform_id != NULL:
             props[count] = CL_CONTEXT_PLATFORM
             count += 1
             props[count] = < cl_context_properties > self.platform_id
             count += 1

        if self._gl_context != 0:
             props[count] = < cl_context_properties > CL_CONTEXT_PROPERTY_USE_CGL_SHAREGROUP_APPLE
             count += 1
             props[count] = < cl_context_properties > self._gl_context
             count += 1
             
        if self._gl_sharegroup != 0:
             props[count] = < cl_context_properties > CL_CONTEXT_PROPERTY_USE_CGL_SHAREGROUP_APPLE
             count += 1
             props[count] = < cl_context_properties > self._gl_sharegroup
             count += 1
             
        props[count] = < cl_context_properties > 0
        
        return props
    
    def __repr__(self):
        return '<ContextProperties platform=%r gl_context=%r gl_sharegroup=%r>' % (self.platform, self.gl_context, self.gl_sharegroup)
    
_context_errors = {
                       CL_INVALID_PLATFORM : ('Properties is NULL and no platform could be selected or if ' 
                                              'platform value specified in properties is not a valid platform.'),
                   CL_INVALID_PROPERTY: ('Context property name in properties is not a supported ' 
                                         'property name, if the value specified for a supported property name is not valid, or if the ' 
                                         'same property name is specified more than once.'),
                   CL_INVALID_VALUE: 'pfn_notify is NULL but user_data is not NULL.',
                   CL_INVALID_DEVICE_TYPE :'device_type is not a valid value.',
                   CL_DEVICE_NOT_AVAILABLE : ('No devices that match device_type and property values' 
                                              'specified in properties are currently available.'),
                                               
                   CL_DEVICE_NOT_FOUND: ('No devices that match device_type and property values ' 
                                        'specified in properties were found.'),
                   CL_OUT_OF_RESOURCES: ('There is a failure to allocate resources required by the ' 
                                         'OpenCL implementation on the device.'),
                   CL_OUT_OF_HOST_MEMORY :('There is a failure to allocate resources required by the ' 
                                           'OpenCL implementation on the host'),
                   }
cdef class Context:
    cdef cl_context context_id
    
    def __cinit__(self):
        self.context_id = NULL
        
    def __init__(self, devices=(), device_type=CL_DEVICE_TYPE_DEFAULT, ContextProperties properties=None):
        
        cdef cl_context_properties * props = NULL
        
        if properties is not None:
            props = properties.context_properties()
        
        cdef cl_device_type dtype
        cdef cl_int err_code
        cdef cl_uint num_devices
        cdef cl_device_id * _devices = NULL

        if devices:
            num_devices = len(devices)
            _devices = < cl_device_id *> malloc(num_devices * sizeof(cl_device_id))
            for i in range(num_devices): 
                _devices[i] = DeviceIDFromPyDevice(devices[i])
                 
            self.context_id = clCreateContext(props, num_devices, _devices, NULL, NULL, & err_code)
            
            if _devices != NULL:
                free(_devices)

            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code, _context_errors)
        else:
            dtype = < cl_device_type > device_type
            self.context_id = clCreateContextFromType(props, dtype, NULL, NULL, & err_code)
    
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code, _context_errors)

    
    def __dealloc__(self):
        if self.context_id != NULL:
            clReleaseContext(self.context_id)
        self.context_id = NULL
        
    def __repr__(self):
        return '<opencl.Context>'
    
    def retain(self):
        clRetainContext(self.context_id)

    def release(self):
        clReleaseContext(self.context_id)
    
    property ref_count:
        def __get__(self):
            pass
        
    property num_devices:
        def __get__(self):
            
            cdef cl_int err_code
            cdef cl_uint num_devices
            err_code = clGetContextInfo (self.context_id, CL_CONTEXT_NUM_DEVICES, sizeof(cl_uint), &num_devices, NULL)
            
            if err_code != CL_SUCCESS:
                raise OpenCLException(err_code)
            
            return num_devices
            
    property devices:
        def __get__(self):
            
            cdef cl_int err_code
            cdef size_t num_devices = self.num_devices
            cdef cl_device_id * _devices
    
            _devices = < cl_device_id *> malloc(num_devices * sizeof(cl_device_id))
    
            err_code = clGetContextInfo(self.context_id, CL_CONTEXT_DEVICES, num_devices*sizeof(cl_device_id), _devices, NULL)
    
            if err_code != CL_SUCCESS:
                free(_devices)
                raise OpenCLException(err_code)
            
            devices = []
            for i in range(num_devices): 
                device_id = _devices[i]
                device = DeviceIDAsPyDevice(device_id)
                devices.append(device) 
                
            free(_devices)
            
            return devices

#===============================================================================
# API
#===============================================================================

cdef api cl_context ContextFromPyContext(object pycontext):
    cdef Context context = < Context > pycontext
    return context.context_id

cdef api object ContextAsPyContext(cl_context context):
    ctx = < Context > Context.__new__(Context)
    clRetainContext(context)
    ctx.context_id = context
    return ctx

cdef api int PyContext_Check(object context):
    return isinstance(context, Context) 