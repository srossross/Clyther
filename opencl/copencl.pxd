
from _cl cimport *
## API FUNCTIONS #### #### #### #### #### #### #### #### #### #### ####
## ############# #### #### #### #### #### #### #### #### #### #### ####
#===============================================================================
# 
#===============================================================================

cdef api cl_platform_id clPlatformFromPyPlatform(object py_platform)

cdef api object clPlatformAs_PyPlatform(cl_platform_id platform_id)

#===============================================================================
# 
#===============================================================================

cdef api cl_device_id CyDevice_GetID(object py_device)

cdef api object DeviceIDAsPyDevice(cl_device_id device_id)

#===============================================================================
# 
#===============================================================================
cdef api object cl_eventAs_PyEvent(cl_event event_id)
cdef api cl_event cl_eventFrom_PyEvent(object event)
cdef api object PyEvent_New(cl_event event_id)
cdef api int PyEvent_Check(object event)

## ############# #### #### #### #### #### #### #### #### #### #### ####

