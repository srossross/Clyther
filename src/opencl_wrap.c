//
// Created on Mar 15, 2010 by GeoSpin Inc
// @author: Sean Ross-Ross srossross@geospin.ca
// website: www.geospin.ca
//
//================================================================================//
// Copyright 2009 GeoSpin Inc.                                                    //
//                                                                                //
// Licensed under the Apache License, Version 2.0 (the "License");                //
// you may not use this file except in compliance with the License.               //
// You may obtain a copy of the License at                                        //
//                                                                                //
//      http://www.apache.org/licenses/LICENSE-2.0                                //
//                                                                                //
// Unless required by applicable law or agreed to in writing, software            //
// distributed under the License is distributed on an "AS IS" BASIS,              //
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.       //
// See the License for the specific language governing permissions and            //
// limitations under the License.                                                 //
//================================================================================//


#define CLyther_MODULE
#include "pyopencl.h"

/* This is a hack to get my editor to work properly*/
#ifndef PyObject_HEAD_INIT(type)
#define PyObject_HEAD_INIT( XXX )
#endif
/* end of hack*/

//========================================================================================================


static cl_int CyError( cl_int err )
{

	if ( err == CL_SUCCESS )
	{
//		PyErr_SetString( PyExc_Exception, "Unknown OpenCL error" );
		return 0;
	}
	else if ( err == CL_INVALID_DEVICE )
	{
		PyErr_SetString( PyExc_TypeError, "OpenCL: Invalid Device" );
		return 1;
	}
	else if ( err == CL_INVALID_VALUE )
	{
		PyErr_SetString( PyExc_TypeError, "OpenCL: Invalid value" );
		return 1;
	}
	else if ( err == CL_INVALID_DEVICE )
	{
		PyErr_SetString( PyExc_TypeError, "OpenCL: Invalid Device" );
		return 1;
	}
	else if ( err == CL_INVALID_CONTEXT )
	{
		PyErr_SetString( PyExc_TypeError, "OpenCL: Invalid Context" );
		return 1;
	}
	else if ( err == CL_INVALID_COMMAND_QUEUE )
	{
		PyErr_SetString( PyExc_TypeError, "OpenCL: Invalid CommandQueue" );
		return 1;
	}
	else if ( err == CL_INVALID_QUEUE_PROPERTIES )
	{
		PyErr_SetString( PyExc_Exception, "OpenCL: Invalid CommandQueue Properties" );
		return 1;
	}
	else if ( err == CL_OUT_OF_HOST_MEMORY )
	{
		PyErr_SetString( PyExc_MemoryError, "OpenCL: Out of host memory" );
		return 1;
	}

	// Build program
	else if ( err == CL_INVALID_PROGRAM )
	{
		PyErr_SetString( PyExc_TypeError, "OpenCL: Invalid program" );
		return 1;
	}

	else if ( err == CL_INVALID_BINARY )
	{
		PyErr_SetString( PyExc_TypeError, "OpenCL: Invalid binary" );
		return 1;
	}

	else if ( err == CL_INVALID_BUILD_OPTIONS )
	{
		PyErr_SetString( PyExc_Exception, "OpenCL: Invalid build options" );
		return 1;
	}

	else if ( err == CL_INVALID_OPERATION )
	{
		PyErr_SetString( PyExc_Exception, "OpenCL: Invalid operation" );
		return 1;
	}
	else if ( err == CL_COMPILER_NOT_AVAILABLE )
	{
		PyErr_SetString( PyExc_Exception, "OpenCL: Compiler not available" );
		return 1;
	}

	else if ( err == CL_BUILD_PROGRAM_FAILURE )
	{
		PyErr_SetString( PyExc_SyntaxError, "OpenCL: Unknown build program failure" );
		return 1;
	}

	else if ( err == CL_INVALID_PROGRAM_EXECUTABLE )
	{
		PyErr_SetString( PyExc_TypeError, "OpenCL: Invalid program executable" );
		return 1;
	}

	else if ( err == CL_INVALID_KERNEL_NAME )
	{
		PyErr_SetString( PyExc_AttributeError, "OpenCL: Invalid kernel name" );
		return 1;
	}
	else if ( err == CL_INVALID_KERNEL_ARGS )
	{
		PyErr_SetString( PyExc_ValueError, "OpenCL: Invalid kernel args" );
		return 1;
	}

	else if ( err == CL_INVALID_KERNEL )
	{
		PyErr_SetString( PyExc_TypeError, "OpenCL: Invalid kernel" );
		return 1;
	}

	else if ( err == CL_INVALID_KERNEL_DEFINITION )
	{
		PyErr_SetString( PyExc_Exception, "OpenCL: Invalid kernel definition" );
		return 1;
	}
	 // buffer objects
	else if ( err == CL_INVALID_BUFFER_SIZE )
	{
		PyErr_SetString( PyExc_ValueError, "OpenCL: Invalid buffer size" );
		return 1;
	}

	else if ( err == CL_DEVICE_MAX_MEM_ALLOC_SIZE )
	{
		PyErr_SetString( PyExc_MemoryError, "OpenCL: device max memory alloc size" );
		return 1;
	}
	else if ( err == CL_INVALID_HOST_PTR )
	{
		PyErr_SetString( PyExc_TypeError, "OpenCL: Invalid host pointer" );
		return 1;
	}

	else if ( err == CL_INVALID_WORK_DIMENSION )
	{
		PyErr_SetString( PyExc_ValueError, "OpenCL: Invalid work dimension" );
		return 1;
	}
	else if ( err == CL_INVALID_WORK_GROUP_SIZE )
	{
		PyErr_SetString( PyExc_ValueError, "OpenCL: Invalid work group size" );
		return 1;
	}

	else if ( err == CL_INVALID_WORK_ITEM_SIZE )
	{
		PyErr_SetString( PyExc_ValueError, "OpenCL: Invalid work item size" );
		return 1;
	}

	else if ( err == CL_INVALID_GLOBAL_OFFSET )
	{
		PyErr_SetString( PyExc_ValueError, "OpenCL: Invalid global offset" );
		return 1;
	}
	else if ( err == CL_OUT_OF_RESOURCES )
	{
		PyErr_SetString( PyExc_MemoryError, "OpenCL: Out of resources" );
		return 1;
	}
	else if ( err == CL_DEVICE_MAX_READ_IMAGE_ARGS )
	{
		PyErr_SetString( PyExc_Exception, "OpenCL: Device max read image args" );
		return 1;
	}

	else if ( err == CL_MEM_OBJECT_ALLOCATION_FAILURE )
	{
		PyErr_SetString( PyExc_MemoryError, "OpenCL: Memory object allocation failure" );
		return 1;
	}

	else if ( err == CL_INVALID_EVENT_WAIT_LIST )
	{
		PyErr_SetString( PyExc_ValueError, "OpenCL: Invalid event wait list" );
		return 1;
	}
	else if ( err == CL_PROFILING_INFO_NOT_AVAILABLE )
	{
		PyErr_SetString( PyExc_Exception, "OpenCL: Profiling info not available" );
		return 1;
	}
	else
	{
		char msg[80];
		snprintf( msg, sizeof(msg), "OpenCL: Unknown OpenCL error %d", err );
//		PyErr_SetString( PyExc_Exception, msg );
		PyErr_SetObject( PyExc_Exception, Py_BuildValue("(si)", msg, err) );
		return 1;
	}

	return 0;

}

static
char* get_command_type_name( cl_command_type ctype )
{
	switch ( ctype )
	{
	case CL_COMMAND_NDRANGE_KERNEL:
		return "ndrange_kernel";

	case CL_COMMAND_TASK: return "task";
	case CL_COMMAND_NATIVE_KERNEL: return "native_kernel";

	case CL_COMMAND_READ_BUFFER: return "read_buffer";
	case CL_COMMAND_WRITE_BUFFER: return "write_buffer";
	case CL_COMMAND_COPY_BUFFER: return "copy_buffer";

	case CL_COMMAND_READ_IMAGE: return "read_image";
	case CL_COMMAND_WRITE_IMAGE: return "write_image";
	case CL_COMMAND_COPY_IMAGE: return "copy_image";

	case CL_COMMAND_COPY_BUFFER_TO_IMAGE: return "copy_buffer_to_image";
	case CL_COMMAND_COPY_IMAGE_TO_BUFFER: return "copy_image_to_buffer";

	case CL_COMMAND_MAP_BUFFER: return "map_buffer";
	case CL_COMMAND_MAP_IMAGE: return "map_image";
	case CL_COMMAND_UNMAP_MEM_OBJECT: return "umap_mem_object";

	case CL_COMMAND_MARKER: return "marker";
	case CL_COMMAND_ACQUIRE_GL_OBJECTS: return "aquire_gl_objects";
	case CL_COMMAND_RELEASE_GL_OBJECTS: return "release_gl_objects";
	}

	return "error: unknown command type";
}

static
char* get_event_status_name( cl_int stat )
{
	switch ( stat )
	{
	case CL_QUEUED:
		return "queued";
	case CL_SUBMITTED:
		return "submitted";
	case CL_RUNNING:
		return "running";
	case CL_COMPLETE:
		return "complete";
	}

	return "error:unknown status";

}


//static void Python_pfn_notify( const char *errinfo, const void *private_info, size_t cb, void *user_data )
//{
//	PyGILState_STATE gstate = PyGILState_Ensure();
//
//
//	PyObject* pfn_notify = PySequence_GetItem( (PyObject*) user_data, 0 );
//	PyObject* pdata = PySequence_GetItem( (PyObject*) user_data, 1 );
//
////	PyObject* pinfo = PyCObject_FromVoidPtr( private_info , NULL );
//	PyObject_CallFunction( pfn_notify, "Os", pdata, errinfo );
//
//	PyGILState_Release(gstate);
//
//	return;
//}



//========================================================================================================
//========================================================================================================
// Device
//========================================================================================================
//========================================================================================================

static const char*
CyDevice_TypeToString( cl_device_type param_value )
{
	switch (param_value)
	{
	case CL_DEVICE_TYPE_CPU :
		return "CPU" ;
		break;
	case CL_DEVICE_TYPE_GPU :
		return  "GPU" ;
		break;
	case CL_DEVICE_TYPE_ACCELERATOR :
		return "ACCELERATOR";
		break;
	case CL_DEVICE_TYPE_DEFAULT :
		return "DEFAULT";
		break;
	default:
		return "ERROR";

	}

}


static int
CyDevice_Init( PyObject *self, PyObject *args, PyObject *kw )
{
	PyErr_SetString( PyExc_Exception, "OpenCL: Can not initialize devices" );
	return -1;
}

static PyObject *
CyDevice_repr( CyDeviceObject * self )
{


	cl_device_type param_value;
	cl_int err;

	char vendor[256];
	char name[256];

	size_t name_size,vendor_size;

	err = clGetDeviceInfo( self->devid, CL_DEVICE_TYPE, sizeof(cl_device_type), &param_value, 0 );
	if ( CyError(err) ) return 0;


	err = clGetDeviceInfo( self->devid, CL_DEVICE_NAME, 256, &name, &name_size );
	if ( CyError(err) ) return 0;
	err = clGetDeviceInfo( self->devid, CL_DEVICE_VENDOR, 256, &vendor, &vendor_size );
	if ( CyError(err) ) return 0;

	name[name_size]=0;
	vendor[vendor_size]=0;

    return PyString_FromFormat( "<copencl.Device type='%s' info='%s: %s'>" , CyDevice_TypeToString( param_value ) ,vendor, name);
}

static PyMethodDef CyDevice_methods[] = {

//        {"rank", (PyCFunction)PyMPI_Comm_rank_M,  METH_NOARGS,
//                "comm.rank() -> int" },
		{NULL}  /* Sentinel */

};



static PyObject*
_CyDevice_Type( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_device_type param_value;

	cl_int err;

	PyObject* result;

	err = clGetDeviceInfo( devid, CL_DEVICE_TYPE, sizeof(cl_device_type), &param_value, 0 );
	if ( CyError(err) ) return 0;


	result = PyString_FromString(CyDevice_TypeToString( param_value ));

	return result;
}

static PyObject*
CyDevice_VendorID( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_uint param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_VENDOR_ID, sizeof(cl_uint), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "I", (unsigned) param_value );
}

static PyObject*
CyDevice_MAX_COMPUTE_UNITS( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_uint param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_MAX_COMPUTE_UNITS, sizeof(cl_uint), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "I", (unsigned) param_value );
}

static PyObject*
CyDevice_MAX_WORK_ITEM_DIMENSIONS( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_uint param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_MAX_WORK_ITEM_DIMENSIONS, sizeof(cl_uint), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "I", (unsigned) param_value );
}


static PyObject*
CyDevice_max_work_item_sizes( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;
	cl_uint param_value;
	size_t *param_value2;
	cl_int err;
	PyObject* t;
	int i;

	err = clGetDeviceInfo( devid, CL_DEVICE_MAX_WORK_ITEM_DIMENSIONS, sizeof(cl_uint), &param_value, 0 );
	if ( CyError(err) ) return 0;

	param_value2 = malloc( param_value*sizeof(size_t) );

	err = clGetDeviceInfo( devid, CL_DEVICE_MAX_WORK_ITEM_SIZES, param_value*sizeof(size_t), param_value2, 0 );
	if ( CyError(err) ) return 0;

	t = PyTuple_New( param_value );
	for (i=0;i< param_value;i++)
	{
		PyTuple_SetItem( t, i, Py_BuildValue( "I", (unsigned) param_value2[i] ) );
	}

	free(param_value2);
	return t;
}

static PyObject*
CyDevice_MAX_WORK_GROUP_SIZE( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;
	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	size_t param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_MAX_WORK_GROUP_SIZE, sizeof(size_t), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "I", (unsigned) param_value );
}


static PyObject*
CyDevice_MAX_CLOCK_FREQUENCY( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_uint param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_MAX_CLOCK_FREQUENCY, sizeof(cl_uint), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "I", (unsigned) param_value );
}
static PyObject*
CyDevice_ADDRESS_BITS( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_uint param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_ADDRESS_BITS, sizeof(cl_uint), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "I", (unsigned) param_value );
}

static PyObject*
CyDevice_MAX_MEM_ALLOC_SIZE( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_ulong param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_MAX_MEM_ALLOC_SIZE, sizeof(cl_ulong), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "k", (unsigned long) param_value );
}

static PyObject*
CyDevice_MAX_PARAMETER_SIZE( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	size_t param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_MAX_PARAMETER_SIZE, sizeof(size_t), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "I", (unsigned) param_value );
}

static PyObject*
CyDevice_MEM_BASE_ADDR_ALIGN( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_uint param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_MEM_BASE_ADDR_ALIGN, sizeof(cl_uint), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "I", (unsigned) param_value );
}

static PyObject*
CyDevice_MIN_DATA_Type_ALIGN_SIZE( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_uint param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_MIN_DATA_TYPE_ALIGN_SIZE, sizeof(cl_uint), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "I", (unsigned) param_value );
}

static PyObject*
CyDevice_GLOBAL_MEM_SIZE( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_ulong param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_GLOBAL_MEM_SIZE, sizeof(cl_ulong), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "k", (unsigned long) param_value );
}

static PyObject*
CyDevice_MAX_CONSTANT_BUFFER_SIZE( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_ulong param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_MAX_CONSTANT_BUFFER_SIZE, sizeof(cl_ulong), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "k", (unsigned long) param_value );
}


static PyObject*
CyDevice_MAX_CONSTANT_ARGS( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_uint param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_MAX_CONSTANT_ARGS, sizeof(cl_uint), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "I", (unsigned) param_value );
}


static PyObject*
CyDevice_LOCAL_MEM_SIZE( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_ulong param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_LOCAL_MEM_SIZE, sizeof(cl_ulong), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "k", (unsigned long) param_value );
}

static PyObject*
CyDevice_ENDIAN_LITTLE( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_bool param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_ENDIAN_LITTLE, sizeof(cl_bool), &param_value, 0 );
	if ( CyError(err) ) return 0;

	if (param_value)
		Py_RETURN_TRUE;
	else
		Py_RETURN_FALSE;
}

static PyObject*
CyDevice_AVAILABLE( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	// clGetDeviceInfo (cl_device_id device, cl_device_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)
	cl_bool param_value;

	cl_int err;

	err = clGetDeviceInfo( devid, CL_DEVICE_AVAILABLE, sizeof(cl_bool), &param_value, 0 );
	if ( CyError(err) ) return 0;

	if (param_value)
		Py_RETURN_TRUE;
	else
		Py_RETURN_FALSE;
}

static PyObject*
CyDevice_NAME( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	cl_int err;

	char c[1024];
	PyObject* s;

	err = clGetDeviceInfo( devid, CL_DEVICE_NAME, 1024, &c, 0 );
	if ( CyError(err) ) return 0;

	s = PyString_FromString( c );
	return s;
}

static PyObject*
CyDevice_VENDOR( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	cl_int err;

	char c[1024];
	PyObject* s;

	err = clGetDeviceInfo( devid, CL_DEVICE_VENDOR, 1024, &c, 0 );
	if ( CyError(err) ) return 0;

	s = PyString_FromString( c );
	return s;
}
static PyObject*
CyDevice_DRIVER_VERSION( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	cl_int err;

	char c[1024];
	PyObject* s;

	err = clGetDeviceInfo( devid, CL_DRIVER_VERSION, 1024, &c, 0 );
	if ( CyError(err) ) return 0;

	s = PyString_FromString( c );
	return s;
}

static PyObject*
CyDevice_PROFILE( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	cl_int err;

	char c[1024];
	PyObject* s;

	err = clGetDeviceInfo( devid, CL_DEVICE_PROFILE, 1024, &c, 0 );
	if ( CyError(err) ) return 0;

	s = PyString_FromString( c );
	return s;
}


static PyObject*
CyDevice_VERSION( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	cl_int err;

	char c[1024];
	PyObject* s;

	err = clGetDeviceInfo( devid, CL_DEVICE_VERSION, 1024, &c, 0 );
	if ( CyError(err) ) return 0;

	s = PyString_FromString( c );
	return s;
}

static PyObject*
CyDevice_QUEUE_PROPERTIES( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	cl_int err;

	cl_command_queue_properties value;

	err = clGetDeviceInfo( devid, CL_DEVICE_QUEUE_PROPERTIES, sizeof(cl_command_queue_properties), &value, 0 );

	if ( CyError(err) ) return 0;


	return Py_BuildValue( "i", (int) value);
}

static PyObject*
CyDevice_EXECUTION_CAPABILITIES( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	cl_int err;

	cl_device_exec_capabilities value;

	err = clGetDeviceInfo( devid, CL_DEVICE_EXECUTION_CAPABILITIES, sizeof(cl_device_exec_capabilities), &value, 0 );

	if ( CyError(err) ) return 0;

	return Py_BuildValue( "i", (int) value );
}

static PyObject*
CyDevice_SUPPORTS_NATIVE_KERNEL( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	cl_int err;

	cl_device_exec_capabilities value;

	err = clGetDeviceInfo( devid, CL_DEVICE_EXECUTION_CAPABILITIES, sizeof(cl_device_exec_capabilities), &value, 0 );

	if ( CyError(err) ) return 0;

	if (value & CL_EXEC_NATIVE_KERNEL )
		Py_RETURN_TRUE;
	else
		Py_RETURN_FALSE;
}

static PyObject*
CyDevice_EXTENSIONS( CyDeviceObject * self, void * x )
{

	cl_device_id devid = self->devid;

	cl_int err;

	char c[2048];
	PyObject* s,* l;

	err = clGetDeviceInfo( devid, CL_DEVICE_EXTENSIONS, 2048, &c, 0 );
	if ( CyError(err) ) return 0;


	s = PyString_FromString( c );

	if (!PyString_Size(s))
	{
		Py_DECREF(s);
		Py_RETURN_NONE;
	}
	else
	{
		l = PyObject_CallMethod( s, "split",0);
		Py_DECREF(s);
		return l;
	}


}


static PyGetSetDef CyDevice_getseters[] = {
    {"type",
     (getter)_CyDevice_Type, (setter)0,
     "type", NULL},

     {"vendor_id",
     (getter)CyDevice_VendorID, (setter)0,
     "A unique device vendor identifier."
     , NULL},
     {"max_compute_units",
     (getter)CyDevice_MAX_COMPUTE_UNITS, (setter)0,
     "max_compute_units", NULL},
     {"max_work_item_dimentions",
     (getter)CyDevice_MAX_WORK_ITEM_DIMENSIONS, (setter)0,
     "max_work_item_dimentions", NULL},

     {"max_work_item_sizes",
     (getter)CyDevice_max_work_item_sizes, (setter)0,
     "max_work_item_sizes", NULL},

     {"max_work_group_size",
     (getter)CyDevice_MAX_WORK_GROUP_SIZE, (setter)0,
     "max_work_group_size", NULL},

     {"max_clock_frequency",
     (getter)CyDevice_MAX_CLOCK_FREQUENCY, (setter)0,
     "max_clock_frequency", NULL},

     {"address_bits",
     (getter)CyDevice_ADDRESS_BITS, (setter)0,
     "address_bits", NULL},

     {"max_mem_alloc_size",
     (getter)CyDevice_MAX_MEM_ALLOC_SIZE, (setter)0,
     "max_mem_alloc_size", NULL},

     {"max_parameter_size",
     (getter)CyDevice_MAX_PARAMETER_SIZE, (setter)0,
     "max_mem_alloc_size", NULL},

     {"mem_base_addr_align",
     (getter)CyDevice_MEM_BASE_ADDR_ALIGN, (setter)0,
     "mem_base_addr_align", NULL},

     {"min_data_type_align_size",
     (getter)CyDevice_MIN_DATA_Type_ALIGN_SIZE, (setter)0,
     "min_data_type_align_size", NULL},

     {"global_mem_size",
     (getter)CyDevice_GLOBAL_MEM_SIZE, (setter)0,
     "global_mem_size", NULL},

     {"max_constant_buffer_size",
     (getter)CyDevice_MAX_CONSTANT_BUFFER_SIZE, (setter)0,
      "max_constant_buffer_size", NULL},

     {"max_constant_args",
     (getter)CyDevice_MAX_CONSTANT_ARGS, (setter)0,
      "max_constant_args", NULL},

      {"local_mem_size",
     (getter)CyDevice_LOCAL_MEM_SIZE, (setter)0,
      "local_mem_size", NULL},

      {"endian_little",
     (getter)CyDevice_ENDIAN_LITTLE, (setter)0,
      "endian_little", NULL},

      {"available",
     (getter)CyDevice_AVAILABLE, (setter)0,
      "available", NULL},

      {"name",
     (getter)CyDevice_NAME, (setter)0,
      "name", NULL},

      {"vendor",
     (getter)CyDevice_VENDOR, (setter)0,
     "vendor", NULL},

     {"driver_version",
     (getter)CyDevice_DRIVER_VERSION, (setter)0,
     "driver_version", NULL},

     {"profile",
     (getter)CyDevice_PROFILE, (setter)0,
      "profile", NULL},

     {"version",
     (getter)CyDevice_VERSION, (setter)0,
      "version", NULL},

     {"extensions",
     (getter)CyDevice_EXTENSIONS, (setter)0,
      "extensions", NULL},


    {"queue_properties",
     (getter)CyDevice_QUEUE_PROPERTIES, (setter)0,
      "queue_properties", NULL},

    {"supports_native_kernel",
     (getter)CyDevice_SUPPORTS_NATIVE_KERNEL, (setter)0,
      "supports_native_kernel", NULL},

    {"execution_capabilities",
     (getter)CyDevice_EXECUTION_CAPABILITIES, (setter)0,
      "execution_capabilities", NULL},

     {NULL}
};

static PyTypeObject _CyDeviceType = {
    PyObject_HEAD_INIT(NULL)
    0,                          /*ob_size*/
    "cl.device",             /*tp_name*/
    sizeof(CyDeviceObject),     /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    (destructor)0, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)CyDevice_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE , /*tp_flags*/
    "OpenCL Device objects may not be initialized from python\n\n"
    "",                  /* tp_doc */
    (traverseproc)0,        /* tp_traverse */
    (inquiry)0,             /* tp_clear */
    0,                      /* tp_richcompare */
    0,                      /* tp_weaklistoffset */
    0,                      /* tp_iter */
    0,                      /* tp_iternext */
    CyDevice_methods,             /* tp_methods */
    0,             /* tp_members */
    (PyGetSetDef*)CyDevice_getseters,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)CyDevice_Init,      /* tp_init */
    0,                         /* tp_alloc */
    0,                 /* tp_new */
};


static PyObject *
Py_NewCLDevice( cl_device_id devid )
{
	CyDeviceObject* self;

	self = (CyDeviceObject*)((PyTypeObject*)(&_CyDeviceType))->tp_alloc( ((PyTypeObject*)(&_CyDeviceType)), 0);

    if (self != NULL) {
    	self->devid = devid;
    }

    return (PyObject *)self;
}





//========================================================================================================
//========================================================================================================
// Context
//========================================================================================================
//========================================================================================================

static int
CyContext_traverse(CyContextObject *self, visitproc visit, void *arg)
{
    Py_VISIT(self->data);
    return 0;
}

static int
CyContext_clear(CyContextObject *self)
{
    PyObject *tmp;

    tmp = self->data;
    self->data = NULL;
    Py_XDECREF(tmp);

    return 0;
}

static void
CyContext_dealloc(CyContextObject* self)
{

    clReleaseContext(self->context);

    CyContext_clear( self);

    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
CyContext_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	CyContextObject *self;

    self = (CyContextObject *)type->tp_alloc(type, 0);

    if (self != NULL) {

    	Py_INCREF(Py_None);
    	self->data = Py_None;

    }

    return (PyObject *)self;
}

static PyObject *
CyContext_repr( CyContextObject * obj )
{
    return PyString_FromFormat( "<copencl.Context object>" );
}


static PyMethodDef CyContext_methods[] = {

//        {"create_program", (PyCFunction)CyCreateProgram,  METH_KEYWORDS|METH_VARARGS,
//                "ctx.create_program( source ) -> Program" },
		{NULL}  /* Sentinel */

};


static PyObject*
CyContext_get_CONTEXT_DEVICES( CyContextObject * self, void * x )
{

	cl_device_id * param_value;
	size_t param_value_size_ret;
	size_t num_devices;
	cl_int err;
    int i;
    PyObject* result;
    CyDeviceObject* dev;

	err = clGetContextInfo( self->context, CL_CONTEXT_DEVICES, 0, 0, &param_value_size_ret );
	if ( CyError(err) ) return 0;

	num_devices = param_value_size_ret/ sizeof( cl_device_id );

	param_value = malloc( param_value_size_ret);

	err = clGetContextInfo( self->context, CL_CONTEXT_DEVICES, param_value_size_ret, param_value, 0 );

	if ( CyError(err) )
	{
		free( param_value );
		return 0;
	}



	result = PyTuple_New( num_devices );
	for (i=0;i< num_devices; i++)
	{
		dev = (CyDeviceObject*) CyDeviceType->tp_new( CyDeviceType,0,0 );

//		err = clRetainDevice(param_value[i]);

		if ( CyError(err) )
		{
			Py_DECREF(result);
			free( param_value );
			return 0;
		}
		dev->devid = param_value[i];
		PyTuple_SetItem( result, i, (PyObject*)dev );

	}

	free( param_value );
	return result;

}

static PyGetSetDef CyContext_getseters[] = {

	     {"devices",
	     (getter)CyContext_get_CONTEXT_DEVICES, (setter)0,
	     "devices", NULL},


		{NULL}
};


static int
CyContext_Init( CyContextObject *self, PyObject *args, PyObject *kw )
{
	char *key_words[] = { "devices", NULL };

	PyObject* devices_list;
    PyObject *pdev;

    int i;
    cl_context_properties *props;

	cl_uint num_devices=0;
	cl_device_id *devices=0;
	cl_int errcode_ret=0;

	if (!PyArg_ParseTupleAndKeywords( args, kw, "O", key_words , &devices_list ))
			return -1;


	if ( !PySequence_Check(devices_list) )
	{
		PyErr_SetString( PyExc_ValueError, "argument 'devices_list' must be a list");
		return -1;
	}

	num_devices = PySequence_Length( devices_list );
	devices = malloc( num_devices* sizeof(cl_device_id) );
	for( i=0;i<num_devices;i++)
	{
		pdev = PySequence_GetItem( devices_list, i );
		if (! PyObject_TypeCheck( pdev, (PyTypeObject*)(&_CyDeviceType) ) )
		{
			PyErr_SetString( PyExc_ValueError, "first argument must be a list of opencl.device objects");
			free(devices);
			return 0;
		}

		devices[i] = ((CyDeviceObject*)pdev)->devid;
	}

	
	props = NULL;
	self->context = clCreateContext( props, num_devices, devices, 0, 0, &errcode_ret);

	free(devices);

	if ( CyError(errcode_ret) ) return -1;


	return 0;
}

static PyTypeObject _CyContextType = {
    PyObject_HEAD_INIT(NULL)
    0,                          /*ob_size*/
    "cl.Context",             /*tp_name*/
    sizeof(CyContextObject),     /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    (destructor)CyContext_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)CyContext_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC , /*tp_flags*/
    "copencl.Context( devices ) -> context \n\n"
    "An OpenCL context is created with one or more devices. \n"
    "Contexts are used by the OpenCL runtime for managing objects \n"
    "such as command-queues, memory, program and kernel objects \n"
    "and for executing kernels on one or more devices specified \n"
    "in the context.",                  /* tp_doc */
    (traverseproc)CyContext_traverse,        /* tp_traverse */
    (inquiry)CyContext_clear,             /* tp_clear */
    0,                      /* tp_richcompare */
    0,                      /* tp_weaklistoffset */
    0,                      /* tp_iter */
    0,                      /* tp_iternext */
    CyContext_methods,             /* tp_methods */
    0,             /* tp_members */
    (PyGetSetDef*)CyContext_getseters,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)CyContext_Init,      /* tp_init */
    0,                         /* tp_alloc */
    CyContext_new,                 /* tp_new */
};


//static PyObject *
//CyContext_FromContext( cl_context context )
//{
//	CyContextObject* self;
//
//	self = (CyContextObject*)((PyTypeObject*)(&_CyContextType))->tp_alloc( ((PyTypeObject*)(&_CyContextType)), 0);
//
//    if (self != NULL) {
//    	self->context = context;
//    	clRetainContext( context );
//    }
//
//    return (PyObject *)self;
//}

//========================================================================================================
//========================================================================================================
// Program
//========================================================================================================
//========================================================================================================


static int
CyProgram_traverse(CyProgramObject *self, visitproc visit, void *arg)
{
    return 0;
}

static int
CyProgram_clear(CyProgramObject *self)
{
    return 0;
}

static void
CyProgram_dealloc(CyProgramObject* self)
{

	clReleaseProgram(self->program);

    CyProgram_clear( self);

    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
CyProgram_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	CyProgramObject *self;

    self = (CyProgramObject *)type->tp_alloc(type, 0);

    return (PyObject *)self;
}

static PyObject *
CyProgram_repr( CyProgramObject * obj )
{
    return PyString_FromFormat( "<copencl.Program object>" );
}

static PyObject *
Py_clBuildProgram( CyProgramObject * prog, PyObject *args, PyObject *kw )
{
	char *key_words[] = { "device_list", "options", "pfn_notify", NULL };

	PyObject* pdevice_list = NULL;
	char* options = NULL;
	
	cl_uint num_devices;
	cl_device_id *device_list;
	cl_int err;
	int i;

	PyObject* item;

    if (!PyArg_ParseTupleAndKeywords( args, kw, "|O", key_words , &pdevice_list ) )
         return 0;


	if (pdevice_list == NULL)
	{
		num_devices=0;
		device_list=0;
	}
	else
	{
		num_devices = PySequence_Length( pdevice_list );
		device_list = malloc( sizeof(cl_device_id) * num_devices );
		for (i=0; i< num_devices; i++ )
		{
			item = PySequence_GetItem( pdevice_list, i );
			if (!PyObject_TypeCheck( item , (PyTypeObject*)&_CyDeviceType))
			{
				PyErr_SetString( PyExc_TypeError, "device_list must be a list containing Open CL device objects");
				return 0;
			}

			device_list[i] = ((CyDeviceObject*) item )->devid;
		}
	}



//	clBuildProgram (cl_program program, cl_uint num_devices,
//	const cl_device_id *device_list, const char *options, void (*pfn_notify)(cl_program, void *user_data), void *user_data)

	err = clBuildProgram( prog->program , num_devices , device_list , options, 0, 0 );

	if ( CyError( err ) ) return 0;

	Py_RETURN_NONE;
}



static PyObject*
CyProgram_get_BUILD_STATUS( CyProgramObject * self, PyObject* pdevice )
{
    cl_device_id device;
	cl_build_status param_value;
	cl_int err;

	if (!PyObject_TypeCheck( pdevice , (PyTypeObject*)&_CyDeviceType))
	{
		PyErr_SetString( PyExc_TypeError, "device_list must be a list containing Open CL device objects");
		return 0;
	}


	device = ((CyDeviceObject*)pdevice)->devid;

	err = clGetProgramBuildInfo( self->program, device, CL_PROGRAM_BUILD_STATUS, sizeof(cl_build_status) , &param_value, 0);

	if ( CyError(err) ) return 0;

	if ( param_value == CL_BUILD_NONE )
	{
		Py_RETURN_NONE;
	}
	else if (param_value == CL_BUILD_ERROR )
	{
		return Py_BuildValue( "s", "build error" );
	}
	else if (param_value == CL_BUILD_SUCCESS )
	{
		return Py_BuildValue( "s", "build success" );
	}
	else if (param_value == CL_BUILD_IN_PROGRESS )
	{
		return Py_BuildValue( "s", "build in progress" );
	}

	Py_RETURN_NONE;
}

static PyObject*
CyProgram_get_BUILD_LOG( CyProgramObject * self, PyObject* pdevice )
{
    cl_device_id device;

    char* param_value;

    cl_int err;
    size_t param_value_size_ret;
    PyObject* result;

	if (!PyObject_TypeCheck( pdevice , (PyTypeObject*)&_CyDeviceType))
	{
		PyErr_SetString( PyExc_TypeError, "device_list must be a list containing Open CL device objects");
		return 0;
	}


	device = ((CyDeviceObject*)pdevice)->devid;

	err = clGetProgramBuildInfo( self->program, device, CL_PROGRAM_BUILD_LOG, 0, 0, &param_value_size_ret );

	param_value = malloc( param_value_size_ret* sizeof(char));

	err = clGetProgramBuildInfo( self->program, device, CL_PROGRAM_BUILD_LOG, param_value_size_ret, param_value, &param_value_size_ret );
	if ( CyError(err) ) return 0;

	result = Py_BuildValue( "s", param_value );

	free(param_value );
	return result;
}

static PyMethodDef CyProgram_methods[] = {

        {"build_status", (PyCFunction)CyProgram_get_BUILD_STATUS,  METH_O,
                "prog.build_status( device) -> str" },
        {"build_log", (PyCFunction)CyProgram_get_BUILD_LOG,  METH_O,
        		"prog.build_log( device) -> str" },
        {"build", (PyCFunction)Py_clBuildProgram,  METH_KEYWORDS|METH_VARARGS,
                "prog.build( [device_list], [options], [pfn_notify]) -> None" },
		{NULL}  /* Sentinel */

};

static PyObject*
CyProgram_get_source( CyProgramObject * self, void * x )
{

	cl_program prog = self->program;
	char* param_value;
	PyObject* result;
	cl_int err;
	size_t param_value_size_ret;

	err = clGetProgramInfo( prog, CL_PROGRAM_SOURCE, 0, 0, &param_value_size_ret );

	param_value = malloc( param_value_size_ret* sizeof(char));

	err = clGetProgramInfo( prog, CL_PROGRAM_SOURCE, param_value_size_ret, param_value, &param_value_size_ret );
	if ( CyError(err) ) return 0;

	result = Py_BuildValue( "s", param_value );

	free(param_value );
	return result;
}


static PyGetSetDef CyProgram_getseters[] = {

	     {"source",
	     (getter)CyProgram_get_source, (setter)0,
	     "source", NULL},

		{NULL}
};

static int
CyProgram_Init(CyProgramObject *self, PyObject *args, PyObject *kw )
{
	char *key_words[] = { "context", "source", NULL };

	const char*strings;
	cl_int err;
	CyContextObject *pcontext;

	if (!PyArg_ParseTupleAndKeywords( args, kw, "O!s", key_words , &_CyContextType, &pcontext, &strings ))
			return -1;


	//clCreateProgramWithSource( cl_context context, cl_uint count, const char **strings, const size_t *lengths, cl_int *errcode_ret )

	self->program = clCreateProgramWithSource( pcontext->context, 1, (const char **) &strings, NULL, &err );

	if ( CyError(err) ) return -1;

    if (!self->program )
    {
        PyErr_SetString(PyExc_Exception,"OpenCL: Failed to create compute program!");
        return -1;
    }

	return 0;
}


static PyTypeObject _CyProgramType = {
    PyObject_HEAD_INIT(NULL)
    0,                          /*ob_size*/
    "cl.Program",             /*tp_name*/
    sizeof(CyProgramObject),     /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    (destructor)CyProgram_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)CyProgram_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC , /*tp_flags*/
    "OpenCL Program object"
    "An OpenCL program consists of a set of kernels that are identified \n"
    "as functions declared with the ``__kernel`` \n"
    "qualifier in the program source. \n"
    "OpenCL programs may also contain auxiliary functions and constant \n" 
    "data that can be used by ``__kernel`` functions. \n"
    "The program executable can be generated online or offline by the  \n"
    "OpenCL compiler for the appropriate target device(s). \n"
    ,                  /* tp_doc */
    (traverseproc)CyProgram_traverse,        /* tp_traverse */
    (inquiry)CyProgram_clear,             /* tp_clear */
    0,                      /* tp_richcompare */
    0,                      /* tp_weaklistoffset */
    0,                      /* tp_iter */
    0,                      /* tp_iternext */
    CyProgram_methods,             /* tp_methods */
    0,             /* tp_members */
    (PyGetSetDef*)CyProgram_getseters,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)CyProgram_Init,      /* tp_init */
    0,                         /* tp_alloc */
    CyProgram_new,                 /* tp_new */
};

//========================================================================================================
//========================================================================================================
// MemBuffer
//========================================================================================================
//========================================================================================================


static int
CyMemBuffer_traverse(CyMemBufferObject *self, visitproc visit, void *arg)
{
//	Py_VISIT(self->host_buffer);
    return 0;
}

static int
CyMemBuffer_clear(CyMemBufferObject *self)
{
//    PyObject *tmp;
//
//    tmp = self->host_buffer;
//    self->host_buffer = NULL;
//    Py_XDECREF(tmp);

    return 0;
}

static void
CyMemBuffer_dealloc(CyMemBufferObject* self)
{

	clReleaseMemObject(self->memory);

    CyMemBuffer_clear( self);

    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
CyMemBuffer_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{

	CyMemBufferObject *self;

    self = (CyMemBufferObject *)type->tp_alloc(type, 0);
//
//    if (self != NULL)
//    {
//    	self->host_buffer;
//    }
    return (PyObject *)self;
}

static PyObject *
CyMemBuffer_repr( CyMemBufferObject * self )
{
	size_t param_value;
	cl_int err = clGetMemObjectInfo( self->memory, CL_MEM_SIZE, sizeof(size_t), &param_value, 0 );

	if (err != CL_SUCCESS )
	{
		return PyString_FromFormat( "<copencl.MemBuffer error='INVALID'>");
	}

    return PyString_FromFormat( "<copencl.MemBuffer size=%lu>", (unsigned long)param_value );
}



static PyMethodDef CyMemBuffer_methods[] = {

         // {"get_local_mem_size", (PyCFunction)CyMemBuffer_LOCAL_MEM_SIZE,  METH_O,
         //         "kernel.get_local_mem_size( device ) -> None" },

		{NULL}  /* Sentinel */

};


static PyObject*
CyMemBuffer_get_size( CyMemBufferObject* self, void * x )
{


//	 clGetMemObjectInfo (cl_mem memobj, cl_mem_info param_name,
//	 size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	size_t param_value;
	cl_int err = clGetMemObjectInfo( self->memory, CL_MEM_SIZE, sizeof(size_t), &param_value, 0 );

	if ( CyError(err) ) return 0;

	return Py_BuildValue( "i", (int) param_value );



}


static PyObject*
CyMemBuffer_get_flags( CyMemBufferObject* self, void * x )
{

//	 clGetMemObjectInfo (cl_mem memobj, cl_mem_info param_name,
//	 size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	cl_mem_flags param_value;
	cl_int err = clGetMemObjectInfo( self->memory, CL_MEM_FLAGS, sizeof(cl_mem_flags), &param_value, 0 );

	if ( CyError(err) ) return 0;

	return Py_BuildValue( "n", (Py_ssize_t) param_value );



}


static PyObject*
CyMemBuffer_get_context( CyMemBufferObject* self, void * x )
{

//	 clGetMemObjectInfo (cl_mem memobj, cl_mem_info param_name,
//	 size_t param_value_size, void *param_value, size_t *param_value_size_ret)
    CyContextObject* ctx;
    cl_int err;


	ctx = (CyContextObject*) CyContextType->tp_new( CyContextType,0,0 );

//	cl_context param_value;
	err = clGetMemObjectInfo( self->memory, CL_MEM_CONTEXT, sizeof(cl_context), &ctx->context, 0 );


	if ( CyError(err) ) return 0;

	clRetainContext(ctx->context);

	if ( CyError(err) ) return 0;

	return (PyObject*) ctx;



}

static PyObject*
CyMemBuffer_get_host_pointer( CyMemBufferObject* self, void * x )
{
    //c_api_object = PyCObject_FromVoidPtr((void *)CLyther_API, NULL);

	void * result;
	size_t mem_size;
	cl_int err;

	err = clGetMemObjectInfo( self->memory, CL_MEM_HOST_PTR, sizeof(void *), &result, 0 );
	if ( CyError(err) ) return 0;
	err = clGetMemObjectInfo( self->memory, CL_MEM_SIZE, sizeof(size_t), &mem_size, 0 );
	if ( CyError(err) ) return 0;

    return PyBuffer_FromReadWriteMemory( result, mem_size );
}
static PyObject*
CyMemBuffer_get_map_count( CyMemBufferObject* self, void * x )
{
    //c_api_object = PyCObject_FromVoidPtr((void *)CLyther_API, NULL);

	cl_uint result;
	cl_int err;

	err = clGetMemObjectInfo( self->memory, CL_MEM_MAP_COUNT, sizeof(void *), &result, 0 );
	if ( CyError(err) ) return 0;

    return PyInt_FromLong( result);
}



static PyGetSetDef CyMemBuffer_getseters[] = {

           {"nbytes",
           (getter)CyMemBuffer_get_size, (setter)0,
           "nbytes", NULL},
           {"flags",
           (getter)CyMemBuffer_get_flags, (setter)0,
           "flags", NULL},

           {"context",
           (getter)CyMemBuffer_get_context, (setter)0,
           "context", NULL},
           
//           {"pointer",
//           (getter)CyMemBuffer_get_pointer, (setter)0,
//           "pointer", NULL},

           {"host",
           (getter)CyMemBuffer_get_host_pointer, (setter)0,
           "host", NULL},

           {"map_count",
           (getter)CyMemBuffer_get_map_count, (setter)0,
           "map_count", NULL},

		{NULL}
};

static int
CyMemBuffer_Init(CyMemBufferObject *self, PyObject *args, PyObject *kw )
{


	char *key_words[] = { "context", "flags", "size","host_buffer", NULL };

	cl_int err;
	Py_ssize_t flags;
	Py_ssize_t size;
	void* host_ptr=NULL;
	CyContextObject *pcontext=NULL;

	if (!PyArg_ParseTupleAndKeywords( args, kw, "O!nn|w", key_words , &_CyContextType, &pcontext, &flags, &size, &host_ptr ))
			return -1;

	self->memory = clCreateBuffer( pcontext->context, (cl_mem_flags)flags, size, host_ptr, &err );
	if ( CyError(err) ) return -1;

	return 0;
}


static PyTypeObject _CyMemBufferType = {
    PyObject_HEAD_INIT(NULL)
    0,                          /*ob_size*/
    "copencl.MemBuffer",             /*tp_name*/
    sizeof(CyMemBufferObject),     /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    (destructor)CyMemBuffer_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)CyMemBuffer_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC , /*tp_flags*/
    "copencl.MemBuffer( context, flags, size [, host_buffer] )",                  /* tp_doc */
    (traverseproc)CyMemBuffer_traverse,        /* tp_traverse */
    (inquiry)CyMemBuffer_clear,             /* tp_clear */
    0,                      /* tp_richcompare */
    0,                      /* tp_weaklistoffset */
    0,                      /* tp_iter */
    0,                      /* tp_iternext */
    CyMemBuffer_methods,             /* tp_methods */
    0,             /* tp_members */
    (PyGetSetDef*)CyMemBuffer_getseters,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)CyMemBuffer_Init,      /* tp_init */
    0,                         /* tp_alloc */
    CyMemBuffer_new,                 /* tp_new */
};

//========================================================================================================
//========================================================================================================
// Event
//========================================================================================================
//========================================================================================================


static int
CyEvent_traverse(CyEventObject *self, visitproc visit, void *arg)
{


    return 0;
}

static int
CyEvent_clear(CyEventObject *self)
{
    return 0;
}

static void
CyEvent_dealloc(CyEventObject* self)
{

	clReleaseEvent(self->event);

    CyEvent_clear( self);

    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
CyEvent_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	CyEventObject *self;

    self = (CyEventObject *)type->tp_alloc(type, 0);

    return (PyObject *)self;
}

static PyObject *
CyEvent_repr( CyEventObject * self )
{
	char* type=0;
	char* status=0;

	cl_int param_value;
	cl_command_type ctype;
	cl_int err = clGetEventInfo( self->event, CL_EVENT_COMMAND_EXECUTION_STATUS, sizeof(cl_int), &param_value, 0 );

	if ( CyError(err) )
		return 0;


	err = clGetEventInfo( self->event, CL_EVENT_COMMAND_TYPE, sizeof(cl_command_type), &ctype, 0 );

	if ( CyError(err) )
		return 0;

	type = get_command_type_name( ctype );
	status = get_event_status_name( param_value );


    return PyString_FromFormat( "<cl.Event object type='%s' status='%s'>" ,type, status );
}


static PyObject *
CyEvent_Wait( CyEventObject * obj )
{

	Py_BEGIN_ALLOW_THREADS;

	clWaitForEvents( 1, &(obj->event) );

	Py_END_ALLOW_THREADS;

	Py_RETURN_NONE;
}

static PyMethodDef CyEvent_methods[] = {
        //
         {"wait", (PyCFunction)CyEvent_Wait,  METH_NOARGS,
                 "wait( ) -> None" },

		{NULL}  /* Sentinel */

};



PyObject*
_CyEvent_get_Type( CyEventObject* self, void * x )
{

//	clGetEventInfo (cl_event event, cl_event_info param_name,
//	size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	cl_command_type param_value;
	cl_int err = clGetEventInfo( self->event, CL_EVENT_COMMAND_TYPE, sizeof(cl_command_type), &param_value, 0 );

	if ( CyError(err) )
		return 0;

	return Py_BuildValue( "s", get_command_type_name( param_value ) );

}

PyObject*
CyEvent_get_status( CyEventObject* self, void * x )
{

//	clGetEventInfo (cl_event event, cl_event_info param_name,
//	size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	cl_int param_value;
	cl_int err = clGetEventInfo( self->event, CL_EVENT_COMMAND_EXECUTION_STATUS, sizeof(cl_int), &param_value, 0 );

	if ( CyError(err) )
		return 0;

	return Py_BuildValue( "s", get_event_status_name( param_value ) );

}


PyObject*
CyEvent_PROFILING_COMMAND_QUEUED( CyEventObject* self, void * x )
{

//	clGetEventProfilingInfo (cl_event event, cl_profiling_info param_name,
//	size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	cl_ulong param_value;
	cl_int err = clGetEventProfilingInfo( self->event, CL_PROFILING_COMMAND_QUEUED, sizeof(cl_ulong), &param_value, 0 );

	if ( CyError(err) )
		return 0;

	return Py_BuildValue( "n",(Py_ssize_t) param_value );

}
PyObject*
CyEvent_PROFILING_COMMAND_SUBMIT( CyEventObject* self, void * x )
{

//	clGetEventProfilingInfo (cl_event event, cl_profiling_info param_name,
//	size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	cl_ulong param_value;
	cl_int err = clGetEventProfilingInfo( self->event, CL_PROFILING_COMMAND_SUBMIT, sizeof(cl_ulong), &param_value, 0 );

	if ( CyError(err) )
		return 0;

	return Py_BuildValue( "n",(Py_ssize_t) param_value );

}
PyObject*
CyEvent_PROFILING_COMMAND_START( CyEventObject* self, void * x )
{

//	clGetEventProfilingInfo (cl_event event, cl_profiling_info param_name,
//	size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	cl_ulong param_value;
	cl_int err;

	err = clGetEventProfilingInfo( self->event, CL_PROFILING_COMMAND_START, sizeof(cl_ulong), &param_value, 0 );
	if ( CyError(err) ) return 0;

	return Py_BuildValue( "n", (Py_ssize_t)param_value );

}
PyObject*
CyEvent_PROFILING_COMMAND_END( CyEventObject* self, void * x )
{

//	clGetEventProfilingInfo (cl_event event, cl_profiling_info param_name,
//	size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	cl_ulong param_value;
	cl_int err;


	err = clGetEventProfilingInfo( self->event, CL_PROFILING_COMMAND_END, sizeof(cl_ulong), &param_value, 0 );
	if ( CyError(err) ) return 0;


	return Py_BuildValue( "n", (Py_ssize_t)param_value );

}


static PyGetSetDef CyEvent_getseters[] = {

          {"type",
          (getter)_CyEvent_get_Type, (setter)0,
          "type", NULL},
          {"status",
          (getter)CyEvent_get_status, (setter)0,
          "status", NULL},

          {"profile_queued",
          (getter)CyEvent_PROFILING_COMMAND_QUEUED, (setter)0,
          "profile_queued", NULL},

          {"profile_submit",
          (getter)CyEvent_PROFILING_COMMAND_SUBMIT, (setter)0,
          "profile_submit", NULL},

          {"profile_start",
          (getter)CyEvent_PROFILING_COMMAND_START, (setter)0,
          "profile_start", NULL},

          {"profile_end",
          (getter)CyEvent_PROFILING_COMMAND_END, (setter)0,
          "profile_end", NULL},

		{NULL}
};

static int
CyEvent_Init( PyObject *self, PyObject *args, PyObject *kw )
{
	PyErr_SetString( PyExc_Exception, "OpenCL: Can not initialize event objects" );
	return -1;
}


static PyTypeObject _CyEventType = {
    PyObject_HEAD_INIT(NULL)
    0,                          /*ob_size*/
    "copencl.Event",             /*tp_name*/
    sizeof(CyEventObject),     /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    (destructor)CyEvent_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)CyEvent_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC , /*tp_flags*/
    "Python can not create event objects \n\n"
    "An event object can be used to track the execution status of a command. \n"
    "The API calls that enqueue commands to a command-queue create a new \n"
    "event object that is returned in the event argument. In case of an error\n"
    " enqueuing the command in the command-queue the event argument does not \n"
    "return an event object.\n\n"
    ""
    "If the execution of a command is terminated, the command-queue associated \n"
    "with this terminated command, and the associated context (and all other \n"
    "command-queues in this context) may no longer be available. The behavior \n"
    "of OpenCL API calls that use this context (and command-queues associated \n"
    "with this context) are now considered to be implementation- defined. \n"
    "The user registered callback function specified when context is created \n"
    "can be used to report appropriate error information.",                  /* tp_doc */
    (traverseproc)CyEvent_traverse,        /* tp_traverse */
    (inquiry)CyEvent_clear,             /* tp_clear */
    0,                      /* tp_richcompare */
    0,                      /* tp_weaklistoffset */
    0,                      /* tp_iter */
    0,                      /* tp_iternext */
    CyEvent_methods,             /* tp_methods */
    0,             /* tp_members */
    (PyGetSetDef*)CyEvent_getseters,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)CyEvent_Init,      /* tp_init */
    0,                         /* tp_alloc */
    CyEvent_new,                 /* tp_new */
};

static PyObject*
CyEvent_New( void )
{
	PyObject* pevent = _CyEventType.tp_new( (PyTypeObject *)&_CyEventType, 0, 0 );
	return pevent;
}




//========================================================================================================
//========================================================================================================
// Kernel
//========================================================================================================
//========================================================================================================


static int
CyKernel_traverse(CyKernelObject *self, visitproc visit, void *arg)
{
    return 0;
}

static int
CyKernel_clear(CyKernelObject *self)
{
    return 0;
}

static void
CyKernel_dealloc(CyKernelObject* self)
{

	clReleaseKernel(self->kernel);

    CyKernel_clear( self);

    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
CyKernel_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	CyKernelObject *self;

    self = (CyKernelObject *)type->tp_alloc(type, 0);

    return (PyObject *)self;
}

static PyObject *
CyKernel_repr( CyKernelObject * self )
{
	char* param_value;

	cl_int err;
	size_t param_value_size_ret;
	PyObject* repr;
//		clGetKernelInfo (cl_kernel kernel, cl_kernel_info param_name,size_t param_value_size, void *param_value, size_t *param_value_size_ret)


	err = clGetKernelInfo( self->kernel, CL_KERNEL_FUNCTION_NAME, 0, 0, &param_value_size_ret );

	param_value = malloc( param_value_size_ret* sizeof(char));

	err = clGetKernelInfo( self->kernel, CL_KERNEL_FUNCTION_NAME, param_value_size_ret, param_value, &param_value_size_ret );
	if ( CyError(err) ) return 0;


	repr = PyString_FromFormat( "<copencl.Kernel object name='%s'>" , param_value );
	free(param_value );

	return repr;
}

static PyObject *
Py_Kernel_SetArgPtr( CyKernelObject * self, PyObject* args, PyObject* kw )
{

	char *key_words[] = { "index", "size", "ptr", NULL };

	int arg_index;
	Py_ssize_t arg_size=0;
	Py_ssize_t  arg_value=0;
	void* arg_ptr;

	if (!PyArg_ParseTupleAndKeywords( args, kw, "inn", key_words , &arg_index, &arg_size , &arg_value ))
			return 0;

	if ( arg_value == 0 ||  arg_size == 0)
	{
		// __local memory
		clSetKernelArg( self->kernel, arg_index, arg_size, NULL );
	}
	
    arg_ptr = (void*) arg_value;
    
	clSetKernelArg( self->kernel, arg_index, arg_size, arg_ptr );
//
	Py_RETURN_NONE;
}

static PyObject *
CyKernel_SetArg( CyKernelObject * self, PyObject* args, PyObject* kw )
{
	char *key_words[] = { "index", "value", "size", NULL };

	int arg_index;
	Py_ssize_t arg_size=0;
	PyObject *arg_value=0;
	const void * arg_buf;
	Py_ssize_t buffer_len;

	if (!PyArg_ParseTupleAndKeywords( args, kw, "iO|n", key_words , &arg_index, &arg_value, &arg_size  ))
			return 0;

	if ( arg_value == Py_None )
	{
		// __local memory
		clSetKernelArg( self->kernel, arg_index, arg_size, NULL );
	}
	else if ( PyObject_TypeCheck( arg_value, (PyTypeObject*)(&_CyMemBufferType) ) )
	{
		clSetKernelArg( self->kernel, arg_index, sizeof(cl_mem), &((CyMemBufferObject*)arg_value)->memory );
	}
	else if (PyObject_CheckReadBuffer(arg_value))
	{
		PyObject_AsReadBuffer( arg_value, &arg_buf, &buffer_len);
		if (arg_size==0)
			buffer_len = buffer_len;

		clSetKernelArg( self->kernel, arg_index, arg_size, arg_buf );
	}
	else
	{
		PyErr_SetString( PyExc_ValueError, "python does not know how to handle this type yet" );
		return 0;
	}

	Py_RETURN_NONE;

}

static PyObject *
CyKernel_WORK_GROUP_SIZE( CyKernelObject * self, PyObject* pdevice )
{
    cl_device_id device;
    size_t param_value;
    cl_int err;

	if (!PyObject_TypeCheck( pdevice , (PyTypeObject*)&_CyDeviceType))
	{
		PyErr_SetString( PyExc_TypeError, "argument must be an Open CL device object");
		return 0;
	}


	device = ((CyDeviceObject*)pdevice)->devid;

//	clGetKernelWorkGroupInfo (cl_kernel kernel, cl_device_id device,
//	cl_kernel_work_group_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	//CL_KERNEL_WORK_GROUP_SIZE
	err = clGetKernelWorkGroupInfo( self->kernel, device, CL_KERNEL_WORK_GROUP_SIZE, sizeof(size_t), &param_value, 0 );

	if ( CyError(err) )
		return 0;

	return Py_BuildValue( "k" , (unsigned long)param_value );


}

static PyObject *
CyKernel_LOCAL_MEM_SIZE( CyKernelObject * self, PyObject* pdevice )
{
    cl_device_id device;
	cl_ulong param_value;
	cl_int err;

	if (!PyObject_TypeCheck( pdevice , (PyTypeObject*)&_CyDeviceType))
	{
		PyErr_SetString( PyExc_TypeError, "argument must be an Open CL device object");
		return 0;
	}


	device = ((CyDeviceObject*)pdevice)->devid;

	err = clGetKernelWorkGroupInfo( self->kernel, device, CL_KERNEL_LOCAL_MEM_SIZE, sizeof(cl_ulong), &param_value, 0 );

	if ( CyError(err) )
		return 0;

	return Py_BuildValue( "k" , (unsigned long)param_value );


}

static PyObject *
CyKernel_CWORK_GROUP_SIZE( CyKernelObject * self, PyObject* pdevice )
{
    cl_device_id device;
	size_t param_value[3];
	cl_int err;

	if (!PyObject_TypeCheck( pdevice , (PyTypeObject*)&_CyDeviceType))
	{
		PyErr_SetString( PyExc_TypeError, "argument must be an Open CL device object");
		return 0;
	}


	device = ((CyDeviceObject*)pdevice)->devid;


//	clGetKernelWorkGroupInfo (cl_kernel kernel, cl_device_id device,
//	cl_kernel_work_group_info param_name, size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	//CL_KERNEL_WORK_GROUP_SIZE
	err = clGetKernelWorkGroupInfo( self->kernel, device, CL_KERNEL_COMPILE_WORK_GROUP_SIZE, 3*sizeof(size_t), &param_value, 0 );

	if ( CyError(err) )
		return 0;

	return Py_BuildValue( "(kkk)" , (unsigned long)param_value[0], (unsigned long)param_value[1],(unsigned long)param_value[2]);


}


static PyMethodDef CyKernel_methods[] = {
        //
    {"set_arg", (PyCFunction)CyKernel_SetArg,  METH_KEYWORDS|METH_VARARGS,
            "kernel.set_arg( index, value ) -> None" },

    {"set_arg_ptr", (PyCFunction)Py_Kernel_SetArgPtr,  METH_KEYWORDS|METH_VARARGS,
        "kernel.set_arg_ptr( index, size , address ) -> None" },
 
                 
         {"get_work_group_size", (PyCFunction)CyKernel_WORK_GROUP_SIZE,  METH_O,
                 "kernel.get_work_group_size( device ) -> None" },
         {"get_compile_work_group_size", (PyCFunction)CyKernel_CWORK_GROUP_SIZE,  METH_O,
                 "kernel.get_compile_work_group_size( device ) -> None" },
         {"get_local_mem_size", (PyCFunction)CyKernel_LOCAL_MEM_SIZE,  METH_O,
                 "kernel.get_local_mem_size( device ) -> None" },

		{NULL}  /* Sentinel */

};


PyObject*
CyKernel_get_name( CyKernelObject* self, void * x )
{

		char* param_value;

		cl_int err;
		size_t param_value_size_ret;
		PyObject* result;
//		clGetKernelInfo (cl_kernel kernel, cl_kernel_info param_name,size_t param_value_size, void *param_value, size_t *param_value_size_ret)


		err = clGetKernelInfo( self->kernel, CL_KERNEL_FUNCTION_NAME, 0, 0, &param_value_size_ret );

		param_value = malloc( param_value_size_ret* sizeof(char));

		err = clGetKernelInfo( self->kernel, CL_KERNEL_FUNCTION_NAME, param_value_size_ret, param_value, &param_value_size_ret );
		if ( CyError(err) ) return 0;

		result = Py_BuildValue( "s", param_value );

		free(param_value );
		return result;

}

PyObject*
CyKernel_get_NUM_ARGS( CyKernelObject* self, void * x )
{

		cl_uint param_value;
		cl_int err;


//		err = clGetKernelInfo( self->kernel, CL_KERNEL_NUM_ARGS, 0, 0, &param_value_size_ret );

		err = clGetKernelInfo( self->kernel, CL_KERNEL_NUM_ARGS, sizeof(cl_uint), &param_value, 0 );
		if ( CyError(err) ) return 0;


		return Py_BuildValue( "I", (unsigned)param_value );

}


static PyGetSetDef CyKernel_getseters[] = {

          {"name",
          (getter)CyKernel_get_name, (setter)0,
          "name", NULL},
          {"num_args",
          (getter)CyKernel_get_NUM_ARGS, (setter)0,
          "num_args", NULL},

		{NULL}
};

static int
CyKernel_Init(CyKernelObject *self, PyObject *args, PyObject *kw )
{
	char *key_words[] = { "program", "name", NULL };

	const char* kernel_name;
	cl_int err;
	CyProgramObject *pprogram;

	if (!PyArg_ParseTupleAndKeywords( args, kw, "O!s", key_words , &_CyProgramType, &pprogram, &kernel_name ))
			return -1;

        // cl_kernel    clCreateKernel (cl_program program, const char *kernel_name, cl_int *errcode_ret)


	self->kernel = clCreateKernel( pprogram->program, kernel_name, &err );

	if ( CyError(err) ) return -1;

	return 0;
}


static PyTypeObject _CyKernelType = {
    PyObject_HEAD_INIT(NULL)
    0,                          /*ob_size*/
    "copencl.Kernel",             /*tp_name*/
    sizeof(CyKernelObject),     /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    (destructor)CyKernel_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)CyKernel_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC , /*tp_flags*/
    "copencl.Kernel( program, name ) -> kernel\n\n"
    "A kernel is a function declared in a program. A kernel is identified \n"
    "by the __kernel qualifier applied to any function in a program. \n"
    "A kernel object encapsulates the specific __kernel function \n"
    "declared in a program and the argument values to be used \n"
    "when executing this __kernel function.",                  /* tp_doc */
    (traverseproc)CyKernel_traverse,        /* tp_traverse */
    (inquiry)CyKernel_clear,             /* tp_clear */
    0,                      /* tp_richcompare */
    0,                      /* tp_weaklistoffset */
    0,                      /* tp_iter */
    0,                      /* tp_iternext */
    CyKernel_methods,             /* tp_methods */
    0,             /* tp_members */
    (PyGetSetDef*)CyKernel_getseters,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)CyKernel_Init,      /* tp_init */
    0,                         /* tp_alloc */
    CyKernel_new,                 /* tp_new */
};


//========================================================================================================
// CommandQueue
//========================================================================================================
//========================================================================================================

static int
PyWaitList_AsWaitList( PyObject* p_event_wait_list, cl_event **ptr_event_wait_list )
{
	int i;
	PyObject* item;
	int num_events_in_wait_list=0;
	cl_event *event_wait_list=0;

	if ( (p_event_wait_list != NULL) && (!PyObject_Not(p_event_wait_list) ) )
	{
		if ( !PySequence_Check(p_event_wait_list) )
		{

			PyErr_SetString( PyExc_ValueError, "argument 'wait' must be a list of opencl.Event objects");
			return -1;
		}
		num_events_in_wait_list = PySequence_Length( p_event_wait_list );
		event_wait_list = malloc( num_events_in_wait_list * sizeof( cl_event ) );

		for (i=0; i < num_events_in_wait_list; i++ )
		{
			item = PySequence_GetItem( p_event_wait_list, i );

//			if (! PyObject_TypeCheck( item, (PyTypeObject*)(&_CyEventType) ) )
			if (! CyEvent_Check(item) )
			{
				PyErr_SetString( PyExc_ValueError, "argument 'wait' must be a list of opencl.Event objects");
				return -1;
			}

			event_wait_list[i] = CyEvent_AsEvent( item );
		}

		*ptr_event_wait_list = event_wait_list;
		return num_events_in_wait_list;
	}
	else
	{
		*ptr_event_wait_list = 0;
		return 0;
	}

}

static int
CyQueue_traverse(CyQueueObject *self, visitproc visit, void *arg)
{
    return 0;
}

static int
CyQueue_clear(CyQueueObject *self)
{

    return 0;
}

static void
CyQueue_dealloc(CyQueueObject* self)
{

	clReleaseCommandQueue(self->queue);

	CyQueue_clear( self );

    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
CyQueue_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
	CyContextObject *self;

    self = (CyContextObject *)type->tp_alloc(type, 0);

    if (self != NULL) {

//    	Py_INCREF(Py_None);
//    	self->data = Py_None;

    }

    return (PyObject *)self;
}

static PyObject *
CyQueue_repr( CyQueueObject * obj )
{
    return PyString_FromFormat( "<copencl.CommandQueue>" );
}

static PyObject *
CyQueue_enqueue_kernel( CyQueueObject * self, PyObject* args, PyObject* kw )
{

	char *key_words[] = { "kernel", "global_work_size","local_work_size","wait", NULL };

	CyKernelObject* pkernel;

	PyObject* p_global_work_size;
	PyObject* p_local_work_size=NULL;
	PyObject* p_event_wait_list=NULL;
	PyObject* p_event=NULL;


	cl_int err;

	cl_uint work_dim;
	size_t *global_work_size;
	size_t *local_work_size=0;
	cl_uint num_events_in_wait_list=0;
	cl_event *event_wait_list=0;

    int i;
    PyObject* item;

	if (!PyArg_ParseTupleAndKeywords( args, kw, "O!O|OO", key_words , (&_CyKernelType), &pkernel, &p_global_work_size, &p_local_work_size, &p_event_wait_list ))
			return 0;


	if ( !PySequence_Check(p_global_work_size) )
	{
		PyErr_SetString( PyExc_ValueError, "argument 'p_global_work_size' must be a list");
		return 0;
	}

	work_dim = PySequence_Length( p_global_work_size );

	global_work_size = malloc( work_dim * sizeof( size_t ) );

	for (i=0; i < work_dim; i++ )
	{
		item = PySequence_GetItem( p_global_work_size, i);

		global_work_size[i] = PyNumber_AsSsize_t( item, PyExc_TypeError );
		if ( PyErr_Occurred() )
			return 0;
	}

	if ((p_local_work_size != NULL ) && (!PyObject_Not(p_local_work_size) ) )
	{
		if ( !PySequence_Check(p_local_work_size) )
		{
			PyErr_SetString( PyExc_ValueError, "argument 'p_local_work_size' must be a list");
			return 0;
		}

		local_work_size = malloc( work_dim * sizeof( size_t ) );

		for (i=0; i < work_dim; i++ )
		{
			item = PySequence_GetItem( p_local_work_size, i );

			local_work_size[i] = PyNumber_AsSsize_t( item, PyExc_TypeError );
//			printf("setting local_work_size[%i] = %i", i,(int)local_work_size[i]);
			if ( PyErr_Occurred() )
				return 0;
		}
	}

	num_events_in_wait_list = PyWaitList_AsWaitList( p_event_wait_list, &event_wait_list );

	p_event = CyEvent_New();

	err = clEnqueueNDRangeKernel( self->queue, pkernel->kernel, work_dim,0, global_work_size, local_work_size,
								  num_events_in_wait_list,event_wait_list, &CyEvent_AsEvent(p_event) );

	if ( CyError(err) )
	{
		Py_DECREF( p_event );
		return 0;

	}

	return (PyObject*)p_event;

}


static PyObject *
CyQueue_enqueue_task( CyQueueObject * self, PyObject* args, PyObject* kw )
{
//	clEnqueueTask (cl_command_queue command_queue, cl_kernel kernel,
//	cl_uint num_events_in_wait_list, const cl_event *event_wait_list, cl_event *event)

	char *key_words[] = { "kernel", "wait", NULL };

	CyKernelObject* pkernel;

	PyObject* p_event_wait_list=NULL;
	PyObject* p_event=NULL;

	cl_int err;

	cl_uint num_events_in_wait_list=0;
	cl_event *event_wait_list=0;

	if (!PyArg_ParseTupleAndKeywords( args, kw, "O!|O", key_words , (&_CyKernelType), &pkernel, &p_event_wait_list ))
			return 0;


	num_events_in_wait_list = PyWaitList_AsWaitList( p_event_wait_list, &event_wait_list );

	p_event = CyEvent_New();

	err = clEnqueueTask( self->queue, pkernel->kernel,
								  num_events_in_wait_list,event_wait_list, &CyEvent_AsEvent(p_event) );

	if ( CyError(err) )
	{
		Py_DECREF( p_event );
		return 0;

	}
	return (PyObject*)p_event;

}




static PyObject *
CyQueue_EnqueueReadBuffer( CyQueueObject * self, PyObject* args, PyObject* kw )
{

	char *key_words[] = { "buffer", "blocking_read","offset","cb","ptr","wait", NULL };
	// CyMemBuffer_get_size

	CyMemBufferObject *pbuffer=0;
	int blocking_read=0;
	Py_ssize_t offset=0;
	Py_ssize_t cb=0;
	void *ptr=0;
	int num_events_in_wait_list=0;
	cl_event *event_wait_list=0;
	PyObject* p_event_wait_list=0;
	PyObject* p_event=0;
	cl_int err;

	if (!PyArg_ParseTupleAndKeywords( args, kw, "O!|innwO", key_words , (&_CyMemBufferType), &pbuffer,&blocking_read, &offset,&cb, &ptr, &p_event_wait_list))
			return 0;



	num_events_in_wait_list = PyWaitList_AsWaitList( p_event_wait_list, &event_wait_list );


	if (!blocking_read)
	{
		p_event = CyEvent_New();

		err = clEnqueueReadBuffer( self->queue, pbuffer->memory, blocking_read, offset, cb,ptr,
									num_events_in_wait_list,event_wait_list, &CyEvent_AsEvent(p_event)  );

		if ( CyError(err) )
		{
			Py_XDECREF( p_event );
			return 0;
		}

		if (num_events_in_wait_list) free( event_wait_list );

		return (PyObject*)p_event;
	}
	else
	{
		err = clEnqueueReadBuffer( self->queue, pbuffer->memory, blocking_read, offset, cb,ptr, num_events_in_wait_list, event_wait_list, 0 );
		if ( CyError(err) )
		{
			return 0;
		}

		if (num_events_in_wait_list) free( event_wait_list );
		Py_RETURN_NONE;
	}



}

static PyObject *
CyQueue_EnqueueWriteBuffer( CyQueueObject * self, PyObject* args, PyObject* kw )
{

	char *key_words[] = { "buffer", "blocking_read","offset","cb","ptr","wait", NULL };
	// CyMemBuffer_get_size

	CyMemBufferObject *pbuffer=0;
	int blocking_read=0;
	Py_ssize_t offset=0;
	Py_ssize_t cb=0;
	void *ptr=0;
	int num_events_in_wait_list=0;
	cl_event *event_wait_list=0;
	PyObject* p_event_wait_list=0;

	PyObject* p_event=0;
	cl_int err;

	if (!PyArg_ParseTupleAndKeywords( args, kw, "O!|innwO", key_words , (&_CyMemBufferType), &pbuffer,&blocking_read, &offset,&cb, &ptr, &p_event_wait_list))
			return 0;


	num_events_in_wait_list = PyWaitList_AsWaitList( p_event_wait_list, &event_wait_list );


	if (!blocking_read)
	{
		p_event = CyEvent_New();
		err = clEnqueueWriteBuffer( self->queue, pbuffer->memory, blocking_read, offset, cb,ptr,
									num_events_in_wait_list,event_wait_list, &CyEvent_AsEvent(p_event) );
		if ( CyError(err) )
		{
			Py_XDECREF( p_event );
			return 0;
		}
		if (num_events_in_wait_list) free( event_wait_list );

		return (PyObject*)p_event;
	}
	else
	{
		err = clEnqueueWriteBuffer( self->queue, pbuffer->memory, blocking_read, offset, cb,ptr, num_events_in_wait_list, event_wait_list, 0 );
		if ( CyError(err) )
		{
			return 0;
		}
		if (num_events_in_wait_list) free( event_wait_list );

		Py_RETURN_NONE;
	}

    // should not get here
    return 0;

}


static PyObject *
CyQueue_EnqueueCopyBuffer( CyQueueObject * self, PyObject* args, PyObject* kw )
{

	char *key_words[] = { "src", "dst","src_offset","dst_offset","cb","wait", NULL };
	// CyMemBuffer_get_size

	CyMemBufferObject *psrc_buffer=0;
	CyMemBufferObject *pdst_buffer=0;
	Py_ssize_t src_offset=0;
	Py_ssize_t dst_offset=0;
	Py_ssize_t cb=0;
	PyObject* p_event_wait_list=0;


	int num_events_in_wait_list=0;
	cl_event *event_wait_list=0;
	cl_int err;
	PyObject* p_event=0;


	if (!PyArg_ParseTupleAndKeywords( args, kw, "O!O!nnnO", key_words , (&_CyMemBufferType), &psrc_buffer,(&_CyMemBufferType), &pdst_buffer,
			&src_offset,&dst_offset,&cb, &p_event_wait_list))
			return 0;


	num_events_in_wait_list = PyWaitList_AsWaitList( p_event_wait_list, &event_wait_list );


	p_event = CyEvent_New();
	err = clEnqueueCopyBuffer( self->queue, psrc_buffer->memory, pdst_buffer->memory, src_offset, dst_offset, cb,
									num_events_in_wait_list,event_wait_list, &CyEvent_AsEvent(p_event) );
	if ( CyError(err) )
	{
		Py_XDECREF( p_event );
		return 0;
	}
	if (num_events_in_wait_list) free( event_wait_list );

	return (PyObject*)p_event;


}

static PyObject *
CyQueue_EnqueueMapBuffer( CyQueueObject * self, PyObject* args, PyObject* kw )
{


	PyObject *device_buffer=0, *p_event_wait_list=0;
	int blocking=1;
	PyObject* p_blocking=NULL;
	Py_ssize_t flags=CL_MAP_READ|CL_MAP_WRITE,offset=0,cb=0;


	cl_uint num_events_in_wait_list=0;
	cl_event *event_wait_list=0;

	void* result;
	cl_int err;
	PyObject* p_event=0;
	PyObject* buff;
	size_t param_value;
	char *key_words[] = { "device_buffer", "blocking", "flags", "offset","size","wait", NULL };

	if (!PyArg_ParseTupleAndKeywords( args, kw, "O!|OnnnO:enqueue_map_buffer", key_words , (&_CyMemBufferType), &device_buffer, &p_blocking, &flags,
			&offset,&cb, &p_event_wait_list))
			return 0;


	if (p_blocking == NULL || PyObject_Not(p_blocking) )
	{
		blocking = 0;
	}
	else
	{
		blocking = 1;
	}
	if (cb==0)
	{

		cl_int err = clGetMemObjectInfo( CyMemBuffer_AsMemBuffer( device_buffer), CL_MEM_SIZE, sizeof(size_t), &param_value, 0 );

		if ( CyError(err) ) return 0;

		cb = param_value;
	}

	num_events_in_wait_list = PyWaitList_AsWaitList( p_event_wait_list, &event_wait_list );


	if (!blocking)
	{
		p_event = CyEvent_New();

		result = clEnqueueMapBuffer( self->queue, CyMemBuffer_AsMemBuffer(device_buffer) , (cl_bool) blocking,(cl_map_flags) flags,
				(size_t) offset, (size_t) cb,
				num_events_in_wait_list, event_wait_list, &CyEvent_AsEvent(p_event), &err );

		if ( CyError(err) )
		{
			Py_XDECREF( p_event );
			return 0;
		}
	}
	else
	{


		result = clEnqueueMapBuffer( self->queue, CyMemBuffer_AsMemBuffer(device_buffer) , (cl_bool) blocking,(cl_map_flags) flags,
				(size_t) offset, (size_t) cb,
				num_events_in_wait_list, event_wait_list, 0, &err );

		if ( CyError(err) )
		{
			return 0;
		}

		p_event = Py_None;
		Py_INCREF( Py_None );

	}


	buff = PyBuffer_FromReadWriteMemory( result, cb );
	return Py_BuildValue( "(OO)", p_event, buff );


}

static PyObject *
CyQueue_EnqueueUnMapBuffer( CyQueueObject * self, PyObject* args, PyObject* kw )
{
//	clEnqueueUnmapMemObject( (cl_command_queue command_queue, cl_mem memobj,
//void *mapped_ptr, cl_uint num_events_in_wait_list, const cl_event *event_wait_list, cl_event *event) )


	PyObject *device_buffer=0, *p_event_wait_list=0;


	cl_uint num_events_in_wait_list=0;
	cl_event *event_wait_list=0;
	void* host_buffer;
	PyObject* p_event;
	cl_int err;

	char *key_words[] = { "device_buffer", "host_buffer", "wait", NULL };

	if (!PyArg_ParseTupleAndKeywords( args, kw, "O!w|O", key_words , (&_CyMemBufferType), &device_buffer, &host_buffer, &p_event_wait_list))
			return 0;

	num_events_in_wait_list = PyWaitList_AsWaitList( p_event_wait_list, &event_wait_list );

//	clEnqueueUnmapMemObject( (cl_command_queue command_queue, cl_mem memobj,
	//void *mapped_ptr, cl_uint num_events_in_wait_list, const cl_event *event_wait_list, cl_event *event) )

	p_event= CyEvent_New();

	err = clEnqueueUnmapMemObject( self->queue, CyMemBuffer_AsMemBuffer(device_buffer), host_buffer , num_events_in_wait_list, event_wait_list,  &CyEvent_AsEvent(p_event) );

	if ( CyError(err) )
	{
		Py_XDECREF( p_event );
		return 0;
	}

	return p_event;
}

static PyObject*
CyQueue_Flush( CyQueueObject * self )
{

	cl_int err = CL_SUCCESS;

	Py_BEGIN_ALLOW_THREADS;

	err = clFlush( self->queue );

	Py_END_ALLOW_THREADS;

	if ( CyError(err) )
		return 0;

	Py_RETURN_NONE;
}

static PyObject*
CyQueue_Finish( CyQueueObject * self )
{

	cl_int err = CL_SUCCESS;
	Py_BEGIN_ALLOW_THREADS;

	err = clFinish( self->queue );

	Py_END_ALLOW_THREADS;

	if ( CyError(err) )
		return 0;

	Py_RETURN_NONE;
}


static PyObject*
CyCommandQueue_Wait( CyQueueObject * self, PyObject* wait_list )
{

	cl_uint num_events;
	cl_event *event_list;
	cl_int err = CL_SUCCESS;

	num_events = PyWaitList_AsWaitList( wait_list, &event_list );

	Py_BEGIN_ALLOW_THREADS;

	err = clEnqueueWaitForEvents( self->queue, num_events, event_list );

	Py_END_ALLOW_THREADS;

	if ( CyError(err) )
		return 0;

	Py_RETURN_NONE;
}

static PyObject*
CyQueue_Marker( CyQueueObject * self )
{

	PyObject* p_event;
	cl_int err = CL_SUCCESS;

	p_event= CyEvent_New();
	err = clEnqueueMarker( self->queue, &CyEvent_AsEvent(p_event) );

	if ( CyError(err) )
		return 0;

	return p_event;
}


static PyObject*
CyCommandQueue_Barrier( CyQueueObject * self )
{
	cl_int err = CL_SUCCESS;

	err =clEnqueueBarrier( self->queue );

	if ( CyError(err) )
		return 0;

	Py_RETURN_NONE;
}

//typedef struct
//{
//	int a;
//	int b;
//} FOO;
//
//typedef void (*USER_FUNC)(void *);
//
//static
//void python_user_func2( FOO foo )
//{
//	PyGILState_STATE gstate;
//	gstate = PyGILState_Ensure( );
//
////	PyObject* py_fn = PySequence_GetItem( t, 0 );
////	PyObject* pdata = PySequence_GetItem( t, 1 );
//
////	PyObject* pinfo = PyCObject_FromVoidPtr( private_info , NULL );
////	PyObject_CallObject( py_fn, pdata );
////	printf("func =%lu\n", (unsigned long)foo.function);
////	printf("args =%lu\n", (unsigned long)voidp );
//	printf("a,b = %i,%i \n", foo.a, foo.b );
////	PyObject_Print( t , stderr ,0 );
////	PyErr_SetString(PyExc_Exception, "hoy");
//
//	PyGILState_Release(gstate);
//	return;
//}


static PyObject*
CyQueue_EnqueueNativeKernel( CyQueueObject * self, PyObject* args, PyObject* kw )
{


	//clEnqueueNativeKernel (cl_command_queue command_queue, void (*user_func)(void *)
	//void *args, size_t cb_args, cl_uint num_mem_objects, const cl_mem *mem_list, const void **args_mem_loc, cl_uint num_events_in_wait_list, const cl_event *event_wait_list, cl_event *event)

	char *key_words[] = { "user_function", "args", "wait", NULL };
	// CyMemBuffer_get_size

	int num_events_in_wait_list=0;
	cl_event *event_wait_list=0;
	PyObject* p_event_wait_list=0;
	PyObject* user_function=0;
	PyObject* user_args=0;
	cl_int err;
	PyObject* p_event;
	PyObject* t;

	PyErr_SetString( PyExc_ValueError, "this function does not work yet");
	return 0;

	if ( !PyArg_ParseTupleAndKeywords( args, kw, "OO|O:enqueue_native_kernel", key_words , &user_function, &user_args, &p_event_wait_list ) )
			return 0;


	num_events_in_wait_list = PyWaitList_AsWaitList(p_event_wait_list, &event_wait_list );


	p_event = CyEvent_New();

	t = PyTuple_New(2);
	PyTuple_SetItem( t, 0, user_function );
	PyTuple_SetItem( t, 1, user_args );

	//cl_int
	//clEnqueueNativeKernel (cl_command_queue command_queue, void (*user_func)(void *)
	//void *args, size_t cb_args, cl_uint num_mem_objects, const cl_mem *mem_list, const void **args_mem_loc, cl_uint num_events_in_wait_list, const cl_event *event_wait_list, cl_event *event)

//	err = clEnqueueNativeKernel( self->queue, python_user_func, &t, sizeof(PyObject*), 0,0, 0, num_events_in_wait_list, event_wait_list, &p_event->event );
//	printf("calling clEnqueueNativeKernel\n");

//	FOO* foo = malloc( sizeof(FOO) );
//	foo->a=0;
//	foo->b=0;

//	err = clEnqueueNativeKernel( self->queue, (USER_FUNC)&python_user_func2, foo, sizeof(FOO*), 0, 0, 0, 0, 0, &CyEvent_AsEvent(p_event) );
//	err = clEnqueueNativeKernel( self->queue, (USER_FUNC)&python_user_func2, 0, 0, 0, 0, 0, 0, 0, &CyEvent_AsEvent(p_event) );

	if ( CyError(err) )
	{
		printf("error calling clEnqueueNativeKernel\n");
		Py_DECREF( p_event );
		return 0;
	}

//	return (PyObject*)p_event;
	return 0;



}



static PyMethodDef CyQueue_methods[] = {

        {"enqueue_kernel", (PyCFunction)CyQueue_enqueue_kernel,  METH_KEYWORDS|METH_VARARGS,
                "queue.enqueue_kernel( kernel, global_work_size, local_work_size, event_list ) -> event" },
        {"enqueue_task", (PyCFunction)CyQueue_enqueue_task,  METH_KEYWORDS|METH_VARARGS,
                "queue.enqueue_task( kernel, event_list ) -> event" },
        {"enqueue_read_buffer", (PyCFunction)CyQueue_EnqueueReadBuffer,  METH_KEYWORDS|METH_VARARGS,
                "queue.enqueue_read_buffer() -> int" },
        {"enqueue_write_buffer", (PyCFunction)CyQueue_EnqueueWriteBuffer,  METH_KEYWORDS|METH_VARARGS,
                "queue.enqueue_write_buffer( buffer blocking_read=False, offset=0 , wait=[] ) -> event" },

        {"enqueue_native_kernel", (PyCFunction)CyQueue_EnqueueNativeKernel,  METH_KEYWORDS|METH_VARARGS,
                "queue.enqueue_native_kernel( callback_func, args, wait ) -> event" },

        {"enqueue_copy_buffer", (PyCFunction)CyQueue_EnqueueCopyBuffer,  METH_KEYWORDS|METH_VARARGS,
                "queue.enqueue_copy_buffer( src, dst, src_offset, dst_offset, cb, wait ) -> event" },

        {"enqueue_map_buffer", (PyCFunction)CyQueue_EnqueueMapBuffer,  METH_KEYWORDS|METH_VARARGS,
                "queue.enqueue_map_buffer( device_buffer, blocking=False, flags=cl.MAP.READ|cl.MAP.WRITE, offset=0 [, cb, wait ]) -> event" },

        {"enqueue_unmap_buffer", (PyCFunction)CyQueue_EnqueueUnMapBuffer,  METH_KEYWORDS|METH_VARARGS,
                "queue.enqueue_unmap_buffer( device_buffer, host_buffer [, wait ]) -> event" },

        {"wait", (PyCFunction)CyCommandQueue_Wait,  METH_O,
                "queue.wait( events ) -> None" },

        {"marker", (PyCFunction)CyQueue_Marker,  METH_NOARGS,
                "queue.marker( ) -> event" },

        {"barrier", (PyCFunction)CyCommandQueue_Barrier,  METH_NOARGS,
                "queue.barrier( ) -> None" },

        {"flush", (PyCFunction)CyQueue_Flush,  METH_NOARGS,
                "queue.flush( ) -> None" },

        {"finish", (PyCFunction)CyQueue_Finish,  METH_NOARGS,
                "queue.finish( ) -> None" },
		{NULL}  /* Sentinel */

};


static PyObject*
CyQueue_Profile_Enabled( CyQueueObject * self, void * x )
{

	cl_command_queue queue = self->queue;
	cl_command_queue_properties param_value;

	cl_int err;
	err = clGetCommandQueueInfo( queue, CL_QUEUE_PROPERTIES, sizeof(cl_command_queue_properties) ,&param_value, 0 );
	if ( CyError(err) ) return 0;

	if ( param_value & CL_QUEUE_PROFILING_ENABLE )
		Py_RETURN_TRUE;
	else
		Py_RETURN_FALSE;
}

static PyObject*
CyQueue_OUT_OF_ORDER_EXEC_MODE_Enabled( CyQueueObject * self, void * x )
{

	cl_command_queue queue = self->queue;
	cl_command_queue_properties param_value;

	cl_int err;

	err = clGetCommandQueueInfo( queue, CL_QUEUE_PROPERTIES, sizeof(cl_command_queue_properties) ,&param_value, 0 );
	if ( CyError(err) ) return 0;

	if ( param_value & CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE )
		Py_RETURN_TRUE;
	else
		Py_RETURN_FALSE;
}

static PyObject*
Py_clGetCommandQueueInfo_device( CyQueueObject * self, void * x )
{
	cl_command_queue queue = self->queue;
	cl_device_id param_value;

	cl_int err;

	err = clGetCommandQueueInfo( queue, CL_QUEUE_DEVICE, sizeof(cl_device_id) ,&param_value, 0 );

	if ( CyError(err) ) return 0;

	return Py_NewCLDevice( param_value );
}

static PyObject*
Py_clGetCommandQueueInfo_context( CyQueueObject * self, void * x )
{

	//	 clGetMemObjectInfo (cl_mem memobj, cl_mem_info param_name,
	//	 size_t param_value_size, void *param_value, size_t *param_value_size_ret)

		CyContextObject* ctx = (CyContextObject*) CyContextType->tp_new( CyContextType,0,0 );

	//	cl_context param_value;
		cl_int err = clGetCommandQueueInfo( self->queue, CL_QUEUE_CONTEXT, sizeof(cl_context), &ctx->context, 0 );

		if ( CyError(err) ) return 0;


		clRetainContext(ctx->context);

		return (PyObject*) ctx;

}


static PyGetSetDef CyQueue_getseters[] = {

		{"profile_enabled",
	    (getter)CyQueue_Profile_Enabled, (setter)0,
	    "profile_enabled", NULL},

	    {"device",
	    (getter)Py_clGetCommandQueueInfo_device, (setter)0,
	    "device", NULL},

	    {"context",
	    (getter)Py_clGetCommandQueueInfo_context, (setter)0,
	    "context", NULL},

		{"out_of_order_exec_mode_enabled",
	    (getter)CyQueue_OUT_OF_ORDER_EXEC_MODE_Enabled, (setter)0,
	    "out_of_order_exec_mode_enabled", NULL},

		{NULL}
};


static int
CyQueue_Init(CyQueueObject *self, PyObject *args, PyObject *kw )
{
	char *key_words[] = { "context", "device", "out_of_order","profile",NULL };
//
	PyObject* pcontext;
	PyObject* pdevice;
	cl_command_queue_properties props=0;
	int out_of_order_exec=0;
	int profiling=0;

	cl_context context;
	cl_device_id devid;
	cl_int err;

	if (!PyArg_ParseTupleAndKeywords( args, kw, "O!O!|ii", key_words , (&_CyContextType), &pcontext, (&_CyDeviceType), &pdevice, &out_of_order_exec, &profiling))
			return -1;

	if (out_of_order_exec)
		props |= CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE;
	if (profiling)
		props |= CL_QUEUE_PROFILING_ENABLE;

	context = ( (CyContextObject*) pcontext)->context;
	devid = ( (CyDeviceObject*) pdevice)->devid;

	self->queue = clCreateCommandQueue( context, devid, props, &err );
	if ( CyError(err) ) return -1;

	return 0;
}

static PyTypeObject _CyQueueType = {
    PyObject_HEAD_INIT(NULL)
    0,                          /*ob_size*/
    "copencl.CommandQueue",             /*tp_name*/
    sizeof(CyQueueObject),     /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    (destructor)CyQueue_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)CyQueue_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE | Py_TPFLAGS_HAVE_GC , /*tp_flags*/
    "copencl.CommandQueue( context, device [, out_of_order_exec_mode [, profiling]] ) -> queue\n\n"
    "OpenCL objects such as memory, program and kernel \n"
    "objects are created using a context. Operations on \n"
    "these objects are performed using a command-queue. \n"
    "The command-queue can be used to queue a set of \n"
    "operations (referred to as commands) in order. \n"
    "Having multiple command-queues allows applications \n"
    "to queue multiple independent commands without \n"
    "requiring synchronization. Note that this should \n"
    "work as long as these objects are not being shared. \n"
    "Sharing of objects across multiple command-queues \n"
    "will require the application to perform appropriate \n"
    "synchronization.",                  /* tp_doc */
    (traverseproc)CyQueue_traverse,        /* tp_traverse */
    (inquiry)CyQueue_clear,             /* tp_clear */
    0,                      /* tp_richcompare */
    0,                      /* tp_weaklistoffset */
    0,                      /* tp_iter */
    0,                      /* tp_iternext */
    CyQueue_methods,             /* tp_methods */
    0,             /* tp_members */
    (PyGetSetDef*)CyQueue_getseters,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)CyQueue_Init,      /* tp_init */
    0,                         /* tp_alloc */
    CyQueue_new,                 /* tp_new */
};




//========================================================================================================
// Platform
//========================================================================================================
//========================================================================================================

static PyObject *
Cy_Plat_repr( CyPlatformObject * self )
{
	char name[256];
	char version[256];
	size_t  version_size,name_size;
	cl_int err;
	err = clGetPlatformInfo( self->plat, CL_PLATFORM_VERSION, 256, version, &version_size );

	if ( err == CL_INVALID_PLATFORM )
	{
		return PyString_FromFormat( "<INVALID opencl.Platform object>"  );
	}

	err = clGetPlatformInfo( self->plat, CL_PLATFORM_NAME, 256, name, &name_size );

	if ( err == CL_INVALID_PLATFORM )
	{
		return PyString_FromFormat( "<INVALID opencl.Platform object>"  );
	}

	version[version_size] = 0;
	name[name_size] = 0;

    return PyString_FromFormat( "<opencl.Platform object name='%s' version='%s'>" ,name, version );
}

static cl_device_type
PyObject_AsCLDeviceType( PyObject* p_device_type )
{
	if (p_device_type == NULL )
	{
		return CL_DEVICE_TYPE_DEFAULT;
	}
	else if ( PyString_Check( p_device_type ) )
	{
		char* device_type_string = PyString_AS_STRING( p_device_type);

		if ( device_type_string == 0 )
			return CL_DEVICE_TYPE_ALL;
		else if ( strcmp(device_type_string,"CPU") == 0 )
			return  CL_DEVICE_TYPE_CPU;
		else if ( strcmp(device_type_string,"GPU") == 0 )
			return  CL_DEVICE_TYPE_GPU;
		else if ( strcmp(device_type_string,"ACCELERATOR") == 0 )
			return  CL_DEVICE_TYPE_ACCELERATOR;
		else if ( strcmp(device_type_string,"DEFAULT") == 0 )
			return  CL_DEVICE_TYPE_DEFAULT;
		else if ( strcmp(device_type_string,"ALL") == 0 )
			return  CL_DEVICE_TYPE_ALL;
		else
		{
			PyErr_SetString( PyExc_Exception, "Unknown OpenCL device type specifier, must be one of  'CPU', 'GPU', 'ACCELERATOR', 'DEFAULT' or 'ALL'" );
			return 0;
		}

	}
	else if ( PyInt_Check( p_device_type ) )
	{
		return (cl_device_type) PyInt_AsLong( p_device_type );
	}
	else
	{
		PyErr_SetString( PyExc_Exception, "Unknown OpenCL device type specifier, must type srt or int" );
		return 0;
	}

}

//cl_int clGetDeviceIDs (cl_platform_id platform, cl_device_type device_type, cl_uint num_entries, cl_device_id *devices, cl_uint *num_devices)
static PyObject*
Cy_GetDeviceIDs( CyPlatformObject* self , PyObject* args  )
{

	PyObject* p_device_type=0;
	cl_device_type device_type;

    cl_uint num_entries;
    cl_uint num_devices;

    cl_device_id *devices;
    CyDeviceObject * pydev;
    cl_int err;
    PyObject * t;
    unsigned i;

	if (!PyArg_ParseTuple( args, "|O" , &p_device_type ) )
	{
		return NULL;
	}

	device_type = PyObject_AsCLDeviceType( p_device_type );

	if (PyErr_Occurred())
		return 0;


	err = clGetDeviceIDs( self->plat, device_type, 0, 0, &num_devices );

	if ( CyError(err ) )
	{
		return 0;
	}


	num_entries = num_devices;
	devices = malloc( sizeof(cl_device_id)*num_devices );



	err = clGetDeviceIDs( self->plat, device_type, num_entries, devices, &num_devices );


	if ( CyError(err ) )
	{
		return 0;
	}

	t = PyTuple_New( num_devices );


	for (i=0; i< num_devices ; i++)
	{
		pydev = (CyDeviceObject*) _CyDeviceType.tp_new( (PyTypeObject *) &_CyDeviceType, NULL, NULL);

		if ( PyTuple_SetItem( t, i, (PyObject*) pydev  ) ) return 0;

		pydev->devid = devices[i];
	}

	free(devices);
	return t;
}

static PyMethodDef CyPlatform_methods[] = {

        {"get_devices", (PyCFunction)Cy_GetDeviceIDs,  METH_KEYWORDS|METH_VARARGS,
                "plat.get_devices( ) -> list\n"
                "returns a list of devices available on this platform." },
		{NULL}  /* Sentinel */

};

static PyObject*
CyPlatform_Profile(CyPlatformObject * self, void * x )
{
//	cl_int
//	clGetPlatformInfo (cl_platform_id platform, cl_platform_info param_name,
//	size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	cl_platform_id pid = self->plat;

	char info[1024];

	cl_int err;
	size_t param_value_size_ret;

	err = clGetPlatformInfo( pid, CL_PLATFORM_PROFILE, 1024, info, &param_value_size_ret );

	if ( err == CL_INVALID_PLATFORM )
	{
		PyErr_SetString( PyExc_Exception, "invalid OpenCL platform");
		return 0;
	}

	return PyString_FromStringAndSize( info, param_value_size_ret-1);
}

static PyObject*
CyPlatform_Version(CyPlatformObject * self, void * x )
{
//	cl_int
//	clGetPlatformInfo (cl_platform_id platform, cl_platform_info param_name,
//	size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	cl_platform_id pid = self->plat;

	char info[1024];

	cl_int err;
	size_t param_value_size_ret;

	err = clGetPlatformInfo( pid, CL_PLATFORM_VERSION, 1024, info, &param_value_size_ret );

	if ( err == CL_INVALID_PLATFORM )
	{
		PyErr_SetString( PyExc_Exception, "invalid OpenCL platform");
		return 0;
	}

	return PyString_FromStringAndSize( info, param_value_size_ret-1);
}
static PyObject*
CyPlatform_Name(CyPlatformObject * self, void * x )
{
//	cl_int
//	clGetPlatformInfo (cl_platform_id platform, cl_platform_info param_name,
//	size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	cl_platform_id pid = self->plat;

	char info[1024];

	cl_int err;
	size_t param_value_size_ret;

	err = clGetPlatformInfo( pid, CL_PLATFORM_NAME, 1024, info, &param_value_size_ret );

	if ( err == CL_INVALID_PLATFORM )
	{
		PyErr_SetString( PyExc_Exception, "invalid OpenCL platform");
		return 0;
	}

	return PyString_FromStringAndSize( info, param_value_size_ret-1);
}

static PyObject*
CyPlatform_Vendor(CyPlatformObject * self, void * x )
{
//	cl_int
//	clGetPlatformInfo (cl_platform_id platform, cl_platform_info param_name,
//	size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	cl_platform_id pid = self->plat;

	char info[1024];

	cl_int err;
	size_t param_value_size_ret;

	err = clGetPlatformInfo( pid, CL_PLATFORM_VENDOR, 1024, info, &param_value_size_ret );

	if ( err == CL_INVALID_PLATFORM )
	{
		PyErr_SetString( PyExc_Exception, "invalid OpenCL platform");
		return 0;
	}

	return PyString_FromStringAndSize( info, param_value_size_ret-1);
}

static PyObject*
CyPlatform_Extensions(CyPlatformObject * self, void * x )
{
//	cl_int
//	clGetPlatformInfo (cl_platform_id platform, cl_platform_info param_name,
//	size_t param_value_size, void *param_value, size_t *param_value_size_ret)

	cl_platform_id pid = self->plat;

	char info[1024];

	cl_int err;
	size_t param_value_size_ret;

	err = clGetPlatformInfo( pid, CL_PLATFORM_EXTENSIONS, 1024, info, &param_value_size_ret );

	if ( err == CL_INVALID_PLATFORM )
	{
		PyErr_SetString( PyExc_Exception, "invalid OpenCL platform");
		return 0;
	}

	return PyString_FromStringAndSize( info, param_value_size_ret-1);
}

static PyGetSetDef CyPlatform_getseters[] = {
    {"profile",
     (getter)CyPlatform_Profile, (setter)0,
     "profile \n"
     "OpenCL profile string. \n"
     "Returns the profile name supported by the implementation. The profile name returned can be one of the following strings:\n"
     "`FULL_PROFILE`  or `EMBEDDED_PROFILE` \n"
     
     , NULL},
    {"version",
     (getter)CyPlatform_Version, (setter)0,
     "Returns the OpenCL version supported by the implementation.", NULL},

     {"name",
     (getter)CyPlatform_Name, (setter)0,
     "name", NULL},
     {"vendor",
     (getter)CyPlatform_Vendor, (setter)0,
     "vendor", NULL},

     {"extensions",
     (getter)CyPlatform_Extensions, (setter)0,
     "extensions", NULL},

     {NULL}
};

static int
CyPlatform_Init( PyObject *self, PyObject *args, PyObject *kw )
{
	PyErr_SetString( PyExc_Exception, "OpenCL: Can not initialize platform" );
	return -1;
}

static PyTypeObject _CyPlatType = {
    PyObject_HEAD_INIT(NULL)
    0,                          /*ob_size*/
    "copencl.Platform",             /*tp_name*/
    sizeof(CyPlatformObject),     /*tp_basicsize*/
    0,                          /*tp_itemsize*/
    (destructor)0, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc)Cy_Plat_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE , /*tp_flags*/
    "Python can not initialize platform objects",                  /* tp_doc */
    (traverseproc)0,        /* tp_traverse */
    (inquiry)0,             /* tp_clear */
    0,                      /* tp_richcompare */
    0,                      /* tp_weaklistoffset */
    0,                      /* tp_iter */
    0,                      /* tp_iternext */
    CyPlatform_methods,             /* tp_methods */
    0,             /* tp_members */
    (PyGetSetDef*)CyPlatform_getseters,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    (initproc)CyPlatform_Init,      /* tp_init */
    0,                         /* tp_alloc */
    0,                 /* tp_new */
};

//========================================================================================================
//========================================================================================================
// Methods
//========================================================================================================
//========================================================================================================


static PyObject*
Cy_GetPlatformIDs( PyObject* self  )
{

	cl_uint num_entries;
	cl_uint num_platforms;

	cl_platform_id *platforms;
    CyPlatformObject * pyplat;

	cl_int err;
	unsigned i;
	PyObject * t;

	err = clGetPlatformIDs( 0, 0, &num_platforms );
	//printf("num_platforms, %i\n", num_platforms);


	if ( CyError(err ) )
	{
		return 0;
	}

	num_entries = num_platforms;
	platforms = malloc( sizeof(cl_platform_id)*num_entries );


	err = clGetPlatformIDs( num_entries, platforms, &num_platforms );


	if ( CyError(err ) )
	{
		return 0;
	}


	t = PyTuple_New( num_platforms );


	for (i=0; i< num_platforms ; i++)
	{
		pyplat = (CyPlatformObject*) _CyPlatType.tp_new( (PyTypeObject *) &_CyPlatType, NULL, NULL);

		if ( PyTuple_SetItem( t, i, (PyObject*) pyplat  ) ) return 0;

		pyplat->plat = platforms[i];
	}

	free(platforms);
	return t;
}


static PyObject*
Cy_GetDeviceIDs2( PyObject* self , PyObject* args  )
{

	PyObject *p_device_type=0;
	cl_device_type device_type;

    cl_uint num_entries;
    cl_uint num_devices;

    cl_device_id *devices;

    cl_int err;
    CyDeviceObject * pydev;

    // PAK: must select platform first
    cl_platform_id platform = 0;
	unsigned i;
    PyObject * t;

	if (!PyArg_ParseTuple( args, "|O" , &p_device_type ) )
	{
		return NULL;
	}

	device_type = PyObject_AsCLDeviceType( p_device_type );

	if (PyErr_Occurred())
		return 0;


	err = clGetPlatformIDs( 1, &platform, NULL);
	err = clGetDeviceIDs( platform, device_type, 0, 0, &num_devices );
//	if (CyError(err)) return 0;

	num_entries = num_devices;
	devices = malloc( sizeof(cl_device_id)*num_devices );

	err = clGetDeviceIDs( platform, device_type, num_entries, devices, &num_devices );


	if ( CyError(err ) )
	{
		return 0;
	}


	t = PyTuple_New( num_devices );


	for (i=0; i< num_devices ; i++)
	{
		pydev = (CyDeviceObject*) _CyDeviceType.tp_new( (PyTypeObject *) &_CyDeviceType, NULL, NULL);

		if ( PyTuple_SetItem( t, i, (PyObject*) pydev  ) ) return 0;

		pydev->devid = devices[i];
	}

	free(devices);
	return t;
}

//typedef void (* fdef )(int);
//static PyObject*
//Cy_TestCObj( PyObject* self , PyObject* args  )
//{
//	PyObject* pycfunction;
//	fdef cfunction;
//
//	printf("got here\n");
//
//	if (!PyArg_ParseTuple( args, "O" , &pycfunction ) )
//		return NULL;
//
////	if ( !PyCObject_Check( pycfunction ) )
////	{
////		PyErr_SetString( PyExc_Exception , "foo");
////		return 0;
////	}
//	printf("got here\n");
//
//
//	cfunction = (fdef) PyCObject_AsVoidPtr( pycfunction );
//
//	cfunction(1);
//
//	printf("got here\n");
//	return Py_None;
//}

static PyMethodDef opencl_methods[] = {

	{"GetPlatformIDs",  (PyCFunction)Cy_GetPlatformIDs, METH_NOARGS,
	"GetPlatformIDs( ) -> list \n"
	"The list of platforms available can be obtained using the following function."},

	{"get_platforms",  (PyCFunction)Cy_GetPlatformIDs, METH_NOARGS,
	"get_platforms( ) -> list \n"
	"The list of platforms available can be obtained using the following function."},

	{"get_devices",  (PyCFunction)Cy_GetDeviceIDs2, METH_VARARGS,
	"get_devices( ) -> list \n"
	"The list of devices available on a platform can be obtained using the following function."},

//	{"test_cobj",  (PyCFunction)Cy_TestCObj, METH_VARARGS,
//	"test_cobj( ) -> None \n"
//	""},

    {NULL}  /* Sentinel */
};


#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif

static PyMethodDef MEM_functions[] = {
    {NULL, NULL, 0, NULL}
};

static PyObject *
initcopencl_MEM(PyObject* outer)
{
    PyObject *m;
    m = Py_InitModule3((char *) "copencl.MEM", MEM_functions, NULL);
    if (m == NULL) {
        return NULL;
    }

    PyModule_AddIntConstant(m, (char *) "READ_WRITE", CL_MEM_READ_WRITE );
    PyModule_AddIntConstant(m, (char *) "WRITE_ONLY", CL_MEM_WRITE_ONLY );
    PyModule_AddIntConstant(m, (char *) "READ_ONLY", CL_MEM_READ_ONLY );
    PyModule_AddIntConstant(m, (char *) "USE_HOST_PTR", CL_MEM_USE_HOST_PTR );
    PyModule_AddIntConstant(m, (char *) "ALLOC_HOST_PTR", CL_MEM_ALLOC_HOST_PTR );
    PyModule_AddIntConstant(m, (char *) "COPY_HOST_PTR", CL_MEM_COPY_HOST_PTR );

    Py_INCREF(m);
    PyModule_AddObject(outer, (char *) "MEM", m);

    return m;
}


static PyObject *
initcopencl_COMMAND(PyObject* outer)
{
    PyObject *m;
    m = Py_InitModule3((char *) "copencl.COMMAND", MEM_functions, NULL);
    if (m == NULL) {
        return NULL;
    }

    PyModule_AddIntConstant(m, (char *) "NDRANGE_KERNEL", CL_COMMAND_NDRANGE_KERNEL );
    PyModule_AddIntConstant(m, (char *) "TASK", CL_COMMAND_TASK );
    PyModule_AddIntConstant(m, (char *) "NATIVE_KERNEL", CL_COMMAND_NATIVE_KERNEL );

    PyModule_AddIntConstant(m, (char *) "READ_IMAGE", CL_COMMAND_READ_IMAGE );
    PyModule_AddIntConstant(m, (char *) "READ_IMAGE", CL_COMMAND_WRITE_IMAGE );
    PyModule_AddIntConstant(m, (char *) "COPY_IMAGE", CL_COMMAND_COPY_IMAGE );

    PyModule_AddIntConstant(m, (char *) "COPY_BUFFER_TO_IMAGE", CL_COMMAND_COPY_BUFFER_TO_IMAGE );
    PyModule_AddIntConstant(m, (char *) "COPY_IMAGE_TO_BUFFER", CL_COMMAND_COPY_IMAGE_TO_BUFFER );

    PyModule_AddIntConstant(m, (char *) "MAP_BUFFER", CL_COMMAND_MAP_BUFFER );
    PyModule_AddIntConstant(m, (char *) "MAP_IMAGE", CL_COMMAND_MAP_IMAGE );
    PyModule_AddIntConstant(m, (char *) "UNMAP_MEM_OBJECT", CL_COMMAND_UNMAP_MEM_OBJECT );

    PyModule_AddIntConstant(m, (char *) "MARKER", CL_COMMAND_MARKER );
    PyModule_AddIntConstant(m, (char *) "ACQUIRE_GL_OBJECTS", CL_COMMAND_ACQUIRE_GL_OBJECTS );
    PyModule_AddIntConstant(m, (char *) "RELEASE_GL_OBJECTS", CL_COMMAND_RELEASE_GL_OBJECTS );

    Py_INCREF(m);
    PyModule_AddObject(outer, (char *) "COMMAND", m);

    return m;
}


static PyObject *
initcopencl_QUEUE(PyObject* outer)
{
    PyObject *m;
    m = Py_InitModule3((char *) "copencl.QUEUE", MEM_functions, NULL);
    if (m == NULL) {
        return NULL;
    }

    PyModule_AddIntConstant(m, (char *) "OUT_OF_ORDER_EXEC_MODE_ENABLE", CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE );
    PyModule_AddIntConstant(m, (char *) "PROFILING_ENABLE", CL_QUEUE_PROFILING_ENABLE );

    Py_INCREF(m);
    PyModule_AddObject(outer, (char *) "QUEUE", m);

    return m;
}


static PyObject *
initcopencl_DEVICE_TYPE(PyObject* outer)
{
    PyObject *m;
    m = Py_InitModule3((char *) "copencl.DEVICE_TYPE", MEM_functions, NULL);
    if (m == NULL) {
        return NULL;
    }

    PyModule_AddIntConstant(m, (char *) "ALL", CL_DEVICE_TYPE_ALL );
    PyModule_AddIntConstant(m, (char *) "CPU", CL_DEVICE_TYPE_CPU );
    PyModule_AddIntConstant(m, (char *) "GPU", CL_DEVICE_TYPE_GPU );
    PyModule_AddIntConstant(m, (char *) "ACCELERATOR", CL_DEVICE_TYPE_ACCELERATOR );
    PyModule_AddIntConstant(m, (char *) "DEFAULT", CL_DEVICE_TYPE_DEFAULT );

    Py_INCREF(m);
    PyModule_AddObject(outer, (char *) "DEVICE_TYPE", m);

    return m;
}

static PyObject *
initcopencl_EXEC(PyObject* outer)
{
    PyObject *m;
    m = Py_InitModule3((char *) "copencl.EXEC", MEM_functions, NULL);
    if (m == NULL) {
        return NULL;
    }

    PyModule_AddIntConstant(m, (char *) "KERNEL", CL_EXEC_KERNEL );
    PyModule_AddIntConstant(m, (char *) "NATIVE_KERNEL", CL_EXEC_NATIVE_KERNEL );

    Py_INCREF(m);
    PyModule_AddObject(outer, (char *) "EXEC", m);

    return m;
}

static PyObject *
initcopencl_MAP(PyObject* outer)
{
    PyObject *m;
    m = Py_InitModule3((char *) "copencl.MAP", MEM_functions, NULL);
    if (m == NULL) {
        return NULL;
    }

    PyModule_AddIntConstant(m, (char *) "READ", CL_MAP_READ);
    PyModule_AddIntConstant(m, (char *) "WRITE", CL_MAP_WRITE );

    Py_INCREF(m);
    PyModule_AddObject(outer, (char *) "MAP", m);

    return m;
}

/* --- enumerations --- */


PyMODINIT_FUNC
initcopencl(void)
{
//    import_array( );

    PyObject* m;
    PyObject* submodule;
    PyObject* mem_flags;

    PyObject* command_types;
    PyObject* command_queue_properties;

    static void *CLyther_API[ClytherAPI_pointers];
    PyObject *c_api_object;

    _CyPlatType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&_CyPlatType) < 0)
        return;

    _CyDeviceType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&_CyDeviceType) < 0)
        return;

    _CyProgramType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&_CyProgramType) < 0)
        return;


    _CyKernelType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&_CyKernelType) < 0)
        return;

    _CyContextType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&_CyContextType) < 0)
        return;

    _CyQueueType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&_CyQueueType) < 0)
        return;


//    _CyMemBufferType.tp_new = PyType_GenericNew;
    if (PyType_Ready(&_CyMemBufferType) < 0)
        return;


    if (PyType_Ready(&_CyEventType) < 0)
        return;


    m = Py_InitModule3("copencl", opencl_methods,
                       "copencl");


    submodule = initcopencl_MEM( m );
    if (submodule == NULL) {
        return;
    }
    submodule = initcopencl_COMMAND( m );
    if (submodule == NULL) {
        return;
    }
    submodule = initcopencl_QUEUE( m );
    if (submodule == NULL) {
        return;
    }
    submodule = initcopencl_DEVICE_TYPE( m );
    if (submodule == NULL) {
        return;
    }
    submodule = initcopencl_EXEC( m );
    if (submodule == NULL) {
        return;
    }
    submodule = initcopencl_MAP( m );
    if (submodule == NULL) {
        return;
    }

    // ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====
    // Initialize Types
    // ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====

    Py_INCREF(&_CyPlatType);
    PyModule_AddObject(m, "Platform", (PyObject *)&_CyPlatType);

    Py_INCREF(&_CyDeviceType);
    PyModule_AddObject(m, "Device", (PyObject *)&_CyDeviceType);

    Py_INCREF(&_CyProgramType);
    PyModule_AddObject(m, "Program", (PyObject *)&_CyProgramType);


    Py_INCREF(&_CyKernelType);
    PyModule_AddObject(m, "Kernel", (PyObject *)&_CyKernelType);


    Py_INCREF(&_CyContextType);
    PyModule_AddObject(m, "Context", (PyObject *)&_CyContextType);

    Py_INCREF(&_CyQueueType);
    PyModule_AddObject(m, "CommandQueue", (PyObject *)&_CyQueueType);


    Py_INCREF(&_CyMemBufferType);
    PyModule_AddObject(m, "MemBuffer", (PyObject *)&_CyMemBufferType);

    Py_INCREF(&_CyEventType);
    PyModule_AddObject(m, "Event", (PyObject *)&_CyEventType);

    // ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====
    // cl_mem_flags
    // ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====
    mem_flags = PyDict_New( );
    PyDict_SetItemString( mem_flags , "read_write", Py_BuildValue( "n",  (int) CL_MEM_READ_WRITE ) );
    PyDict_SetItemString( mem_flags , "write_only", Py_BuildValue( "n",  (int) CL_MEM_WRITE_ONLY ) );
    PyDict_SetItemString( mem_flags , "read_only", Py_BuildValue( "n",  (int) CL_MEM_READ_ONLY ) );
    PyDict_SetItemString( mem_flags , "use_host_ptr", Py_BuildValue( "n",  (int) CL_MEM_USE_HOST_PTR ) );
    PyDict_SetItemString( mem_flags , "alloc_host_ptr", Py_BuildValue( "n",  (int) CL_MEM_ALLOC_HOST_PTR ) );
    PyDict_SetItemString( mem_flags , "copy_host_ptr", Py_BuildValue( "n",  (int) CL_MEM_COPY_HOST_PTR ) );

    PyModule_AddObject(m, "mem_flags", mem_flags);

    // ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====
    // command_types
    // ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====

    command_types = PyDict_New( );

    PyDict_SetItemString( command_types , "ndrange_kernel", Py_BuildValue( "i",  (int) CL_COMMAND_NDRANGE_KERNEL ) );
    PyDict_SetItemString( command_types , "task", Py_BuildValue( "i",  (int) CL_COMMAND_TASK ) );
    PyDict_SetItemString( command_types , "native_kernel", Py_BuildValue( "i",  (int) CL_COMMAND_NATIVE_KERNEL ) );

    PyDict_SetItemString( command_types , "read_buffer", Py_BuildValue( "i",  (int) CL_COMMAND_READ_BUFFER ) );
    PyDict_SetItemString( command_types , "write_buffer", Py_BuildValue( "i", (int)  CL_COMMAND_WRITE_BUFFER ) );
    PyDict_SetItemString( command_types , "copy_buffer", Py_BuildValue( "i",  (int) CL_COMMAND_COPY_BUFFER ) );

    PyDict_SetItemString( command_types , "read_image", Py_BuildValue( "i",  (int) CL_COMMAND_READ_IMAGE ) );
    PyDict_SetItemString( command_types , "write_image", Py_BuildValue( "i", (int)  CL_COMMAND_WRITE_IMAGE ) );
    PyDict_SetItemString( command_types , "copy_image", Py_BuildValue( "i", (int)  CL_COMMAND_COPY_IMAGE ) );

    PyDict_SetItemString( command_types , "copy_buffer_to_image", Py_BuildValue( "i", (int)  CL_COMMAND_COPY_BUFFER_TO_IMAGE ) );
    PyDict_SetItemString( command_types , "copy_image_to_buffer", Py_BuildValue( "i", (int)  CL_COMMAND_COPY_IMAGE_TO_BUFFER ) );

    PyDict_SetItemString( command_types , "map_buffer", Py_BuildValue( "i", (int)  CL_COMMAND_MAP_BUFFER ) );
    PyDict_SetItemString( command_types , "map_image", Py_BuildValue( "i", (int)  CL_COMMAND_MAP_IMAGE ) );
    PyDict_SetItemString( command_types , "umap_mem_object", Py_BuildValue( "i", (int)  CL_COMMAND_UNMAP_MEM_OBJECT ) );

    PyDict_SetItemString( command_types , "marker", Py_BuildValue( "i", (int)  CL_COMMAND_MARKER ) );
    PyDict_SetItemString( command_types , "aquire_gl_objects", Py_BuildValue( "i", (int)  CL_COMMAND_ACQUIRE_GL_OBJECTS ) );
    PyDict_SetItemString( command_types , "release_gl_objects", Py_BuildValue( "i", (int)  CL_COMMAND_RELEASE_GL_OBJECTS ) );


    PyModule_AddObject(m, "event_command_types", command_types);

    // ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====
    // command_queue_properties
    // ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====
    command_queue_properties = PyDict_New( );

    PyModule_AddObject(m, "command_queue_properties", command_queue_properties );

    PyDict_SetItemString( command_queue_properties , "OUT_OF_ORDER_EXEC_MODE_ENABLE", Py_BuildValue( "i",  CL_QUEUE_OUT_OF_ORDER_EXEC_MODE_ENABLE ) );
    PyDict_SetItemString( command_queue_properties , "PROFILING_ENABLE", Py_BuildValue( "i",  CL_QUEUE_PROFILING_ENABLE ) );


    // ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====
    // CLyther_API
    // ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ==== ====


    /* Initialize the C API pointer array */
    /* Create a CObject containing the API pointer array's address */
    c_api_object = PyCObject_FromVoidPtr((void *)CLyther_API, NULL);

	CLyther_API[0] = CyDeviceType;
	CLyther_API[1] = CyContextType;
	CLyther_API[2] = CyProgramType;
	CLyther_API[3] = CyMemBufferType;

	CLyther_API[4] = CyEventType;
	CLyther_API[5] = CyKernelType;
	CLyther_API[6] = CyQueueType;
	CLyther_API[7] = CyPlatType;

	CLyther_API[8] = (void*)CyError;


    if (c_api_object != NULL)
        PyModule_AddObject(m, "_C_API", c_api_object);

}



