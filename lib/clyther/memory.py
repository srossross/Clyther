'''
Created on Mar 5, 2010 by GeoSpin Inc
@author: Sean Ross-Ross srossross@geospin.ca
website: www.geospin.ca
'''


#================================================================================#
# Copyright 2009 GeoSpin Inc.                                                     #
#                                                                                # 
# Licensed under the Apache License, Version 2.0 (the "License");                #
# you may not use this file except in compliance with the License.               #
# You may obtain a copy of the License at                                        #
#                                                                                #
#      http://www.apache.org/licenses/LICENSE-2.0                                #
#                                                                                #
# Unless required by applicable law or agreed to in writing, software            #
# distributed under the License is distributed on an "AS IS" BASIS,              #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.       #
# See the License for the specific language governing permissions and            #
# limitations under the License.                                                 #
#================================================================================#

import ctypes
from ctypes import c_uint32
import copencl as cl #@UnresolvedImport IGNORE:F0401
from clyther.static import get_context, get_queue
from clyther.api.cltypes import cltype, rtte

    

class array_type( ctypes.Structure, rtte ):
    
    mod = ''
    
    _fields_ = [ 
                ('start',c_uint32* 3),
                ('stop',c_uint32* 3),
                ('step',c_uint32* 3),
                ('shape',c_uint32* 3),
                ('size',c_uint32),
                ]

    def __init__( self, elem_type, shape=None ,start=None, stop=None, step=None ):
        
        self.elem_type = cltype.ctype( elem_type )
        
        size = 1
        if shape is not None:
            for i,item in enumerate(shape):
                self.shape[i] =  c_uint32( int(item) )
                size *= item
                self.stop[i] = self.shape[i]
        
        self.size = c_uint32(int(size))
        
        if start is not None:
            for i,item in enumerate(start):
                self.start[i] =  c_uint32( int(item) )

        if stop is not None:
            for i,item in stop:
                self.stop[i] =  c_uint32( int(stop[i]) )

        if step is not None:
            for i, item in step:
                self.step[i] =  c_uint32( int(item) )
                
#        self.shape = tuple( shape )
    
    
    def cdef(self):
        return '%s %s*' %( self.mod , cltype.cdef( self.elem_type ) )
    
    def _get_ctype(self):
        return self
    
    ctype = property( _get_ctype )
    
#    def __len__(self):
#        return self.shape[0]
    
#    def _get_size(self):
#        if self.shape is None:
#            return self.shape
#        
#        return reduce(lambda x,y: x*y, self.shape )
#    
#    size = property( _get_size )
    
    def __hash__( self ):
        return hash( self.elem_type ) + hash( tuple(self.shape) ) - hash(self.mod) 
   
    def __repr__(self):
        if hasattr(self.elem_type, '__name__'):
            ename = self.elem_type.__name__
        else:
            ename = repr(self.elem_type)
        return '%s( %s, shape=%r )' %(self.__class__.__name__, self.elem_type.__name__, tuple(self.shape))
        
    
class global_array_type( array_type ):
    mod = '__global'
    
    
class shared_array_type( array_type ):
    mod = '__local'


class DeviceBuffer( cl.MemBuffer ):
    
    def __init__(self, shape, elem_type, flags=None, desc=None, context=None , host_buffer=None ):
        
        self.shape = tuple(shape)
        self.elem_type = elem_type
        
        if flags is None:
            flags = cl.MEM.READ_WRITE
            
        if context is None:
            context = get_context( )
            
        # having a little trouble with the C side buffer objects
        if host_buffer is None:
            cl.MemBuffer.__init__( self, context, flags, self.nbytes)
        else:
            cl.MemBuffer.__init__( self, context, flags, self.nbytes, host_buffer=host_buffer)
        
        if desc==None:
            desc = CLMemHelper( (0,0,0),(1,1,1),self.shape,self.shape,self.size )
            
        self.mem_desc = desc
        self.__hosts__ = []
        
    def _get_ptr_type(self):
        return ctypes.POINTER( self.elem_type )
    
    cptr_type = property( _get_ptr_type )
    
    def _get_desc(self):
        return self.mem_desc
    
    desc = property( _get_desc )
    
    def _get_size(self):
        return reduce(lambda x,y: x*y, self.shape )
    
    size = property( _get_size ) 
    
    def _get_nbytes(self):
        
        return self.size * self.itemsize
    
    nbytes = property( _get_nbytes ) 
    
    def _get_itemsize(self):
        return cltype.sizeof( self.elem_type )
    
    itemsize = property( _get_itemsize)
    
    def from_host( self, host_buffer, size=None, queue=False,block=False ):
        
        if size is None:
            nbytes = max(self.nbytes,len(buffer(host_buffer)) )
        else:
            nbytes = size * ctypes.sizeof( self.elem_type )
        
        context = self.context 

        if not queue:
            queue = get_queue( )
        
        event = queue.enqueue_write_buffer( self, block, 0, nbytes, host_buffer )
        
        return event
    
    def to_host(self, host_buffer, size=None, queue=False, block=False ):

        if size is None:
            nbytes = max(self.nbytes,len(buffer(host_buffer)) )
        else:
            nbytes = size * self.itemsize


        if not queue:
            queue = get_queue( )
            
            
        event = queue.enqueue_read_buffer( self, block, 0, nbytes, host_buffer )
        
        return event
    
    def __enter__( self ):
        
        event,host = self.map( )
        
        self.__hosts__.append( host )
        
        event.wait( )
        
        return  host
    
    def __exit__( self, type, value, traceback ):
        
        host = self.__hosts__.pop( )
        
        event = self.unmap( host )
        event.wait( )
        return

    def item( self, queue=None ):
        
        if queue is None:
            queue = get_queue( )
            
        host_result = self.elem_type( )
        
        queue.enqueue_read_buffer( self, True, 0, ctypes.sizeof(self.elem_type), host_result )
        
        if hasattr( host_result, 'value'):
            return host_result.value
        else:
            return host_result
    
    def _get_ctype(self):
        return global_array_type( self.elem_type, self.shape )
    
    ctype = property( _get_ctype )
    
    def map(self,queue=None):
        '''
        returns (event,buffer) tuple
        '''
        if queue is None:
            queue = get_queue( )
        
        result = queue.enqueue_map_buffer(self)
        
        return result
    
    def unmap(self,host, queue=None):
        
        if queue is None:
            queue = get_queue( )
            
        result = queue.enqueue_unmap_buffer(self,host)
        
        return result
    
    
class Shared(object):
    def __init__(self, shape=None, ctype=ctypes.c_char , context=None ):
        
        self._ctx = context
         
        self.elem_type = ctype
        
        device = self.ctx.devices[0]
        local_mem_size = device.local_mem_size
        if shape is None:
            self.shape = (device.local_mem_size // self.itemsize,)
            
        else:
            self.shape = tuple(shape)
            
            if self.nbytes >  local_mem_size:
                raise MemoryError('OpenCL memory error size of local array is too big' )
            
        
    def _get_itemsize(self):
        return ctypes.sizeof(self.elem_type)
    
    itemsize = property( _get_itemsize )
    
    def _get_ptr_type(self):
        return ctypes.POINTER( self.elem_type )
    
    cptr_type = property( _get_ptr_type )

    
    def _get_ctx(self):
        if self._ctx is None:
            return get_context()
        else:
            return self._ctx
        
    def _set_ctx(self,ctx):
        if ctx is None:
            self._ctx =  get_context( )
        else:
            self._ctx = ctx
    
    ctx = property( _get_ctx,_set_ctx )
    
    def _get_size(self):
        
#        local_mem_size = self.ctx.devices[0].local_mem_size
        
        return reduce(lambda x,y:x*y , self.shape)
        
    size = property( _get_size )
    
    def _get_nbytes(self):
        return self.size * self.itemsize 
    
    nbytes = property( _get_nbytes )
    
    def _get_ctype(self):
        return shared_array_type( self.elem_type, self.shape )
    
    ctype = property(_get_ctype )


#def buffer( ):
#    
#    cl.MemBuffer( context, cl.mem_flags['read_write'] )

class CLMemHelper( ctypes.Structure ):
    _fields_ = [ 
                ('start',ctypes.c_uint32* 3),
                ('stop',ctypes.c_uint32* 3),
                ('step',ctypes.c_uint32* 3),
                ('shape',ctypes.c_uint32* 3),
                ('size',ctypes.c_uint32),
                ]
    
