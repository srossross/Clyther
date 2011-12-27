'''
Created on Dec 22, 2011

@author: sean
'''

import opencl as cl
from clyther.array import CLArrayContext
import clyther as cly
import clyther.runtime as clrt
from core import Grid, available 
import numpy



class CLTimeSteper(object):
    DEVICE_TYPE = cl.Device.CPU
    @classmethod
    def create_grid(cls, nx=500, ny=500):
        ca = CLArrayContext(device_type=cls.DEVICE_TYPE)
        g = Grid(ca, nx, ny)
        g.queue = cl.Queue(ca)
        return g

    @classmethod
    def finish(cls, grid):
        grid.queue.finish()
        

class openclCheckerTimeStep(CLTimeSteper):
    @classmethod
    def create_grid(cls, nx=500, ny=500):
        ca = CLArrayContext(device_type=cls.DEVICE_TYPE)
        g = Grid(ca, nx, ny)
        
        dx2, dy2 = g.dx ** 2, g.dy ** 2
        dnr_inv = 0.5 / (dx2 + dy2)
          
        #self.ctx = cl.create_some_context()
    
        g.prg = cl.Program(ca, """
        __kernel void lp2dstep( __global float *u, const uint stidx )
        {          
            int i = get_global_id(0) + 1;
            int ny = %d;
        
            for ( int j = 1 + ( ( i + stidx ) %% 2 ); j<( %d-1 ); j+=2 ) {
                u[ny*j + i] = ((u[ny*(j-1) + i] + u[ny*(j+1) + i])*%g +
                                     (u[ny*j + i-1] + u[ny*j + i + 1])*%g)*%g;
            }
        }""" % (ny, ny, dy2, dx2, dnr_inv))
        
                        
        g.prg.build()

        g.lp2dstep = g.prg.lp2dstep
        
        g.lp2dstep.argnames = 'u', 'stidx'
        g.lp2dstep.argtypes = cl.global_memory(ctype='f'), cl.cl_uint
        g.lp2dstep.global_work_size = [nx - 2]
        
        g.queue = cl.Queue(ca)
        
        return g
    
    
    @classmethod
    def time_step(cls, grid, dt=0.0):
        """
        Takes a time step using a PyOpenCL kernel based on inline C code from:
        http://www.scipy.org/PerformancePython
        The original method has been modified to use a red-black method that is
        more parallelizable.
        """
        nx, ny = grid.u.shape
        
        event = grid.lp2dstep(grid.queue, grid.u, 1)
        grid.queue.enqueue_wait_for_events(event)
        
        event = grid.lp2dstep(grid.queue, grid.u, 2)
        grid.queue.enqueue_wait_for_events(event)
        
@available(True)
class opencl_cpu(openclCheckerTimeStep):
    'opencl-cpu'
    DEVICE_TYPE = cl.Device.CPU



@available(True)
class opencl_gpu(openclCheckerTimeStep):
    'opencl-gpu'
    DEVICE_TYPE = cl.Device.GPU

#===============================================================================
# 
#===============================================================================

@cly.global_work_size(lambda u: [u.shape[0] - 2])
@cly.kernel
def lp2dstep(u, dx2, dy2, dnr_inv, stidx):
    i = clrt.get_global_id(0) + 1
    
    ny = u.shape[1]
    
    for j in range(1 + ((i + stidx) % 2), ny - 1, 2):
        u[j, i] = ((u[j - 1, i] + u[j + 1, i]) * dy2 + 
                   (u[j, i - 1] + u[j, i + 1]) * dx2) * dnr_inv

class clytherCheckerTimeStep(CLTimeSteper):
    @classmethod
    def create_grid(cls, nx=500, ny=500):
        ca = CLArrayContext(device_type=cls.DEVICE_TYPE)
        g = Grid(ca, nx, ny)

        g.queue = cl.Queue(ca)
        
        return g
    
    @classmethod
    def time_step(cls, grid, dt=0.0):
        """
        Takes a time step using a PyOpenCL kernel based on inline C code from:
        http://www.scipy.org/PerformancePython
        The original method has been modified to use a red-black method that is
        more parallelizable.
        """
        dx2, dy2 = grid.dx ** 2, grid.dy ** 2
        dnr_inv = 0.5 / (dx2 + dy2)
        
        event = lp2dstep(grid.queue, grid.u, dx2, dy2, dnr_inv, 1)
        grid.queue.enqueue_wait_for_events(event)
        
        event = lp2dstep(grid.queue, grid.u, dx2, dy2, dnr_inv, 2)
        grid.queue.enqueue_wait_for_events(event)
        
        

@available(True)
class clyther_checker_cpu(clytherCheckerTimeStep):
    'clyther-checker-cpu'
    DEVICE_TYPE = cl.Device.CPU

@available(True)
class clyther_checker_gpu(clytherCheckerTimeStep):
    'clyther-checker-gpu'
    DEVICE_TYPE = cl.Device.GPU


#===============================================================================
# 
#===============================================================================


@cly.task
def cly_time_step_task(u, dy2, dx2, dnr_inv, error):
    # The actual iteration
    nx = u.shape[0] 
    ny = u.shape[1]
    err = 0.0
    for i in range(1, nx - 1):
        for j in range(1, ny - 1):
            tmp = u[i, j]
            u[i, j] = ((u[i - 1, j] + u[i + 1, j]) * dy2 + 
                      (u[i, j - 1] + u[i, j + 1]) * dx2) * dnr_inv
                      
            diff = u[i, j] - tmp
            err += diff * diff
            
    error[0] = err
    

@available(cly is not None)
class clyther_task(CLTimeSteper):
    'clyther-task'
    
    @classmethod
    def time_step(cls, grid, dt=0.0):
        """clyther-task
        Takes a time step using a numeric expressions."""
        g = grid
        dx2, dy2 = g.dx ** 2, g.dy ** 2
        dnr_inv = 0.5 / (dx2 + dy2)
        u = g.u
        
        error = g.np.empty([1], ctype='f')
            
        cly_time_step_task(u.queue, u, dy2, dx2, dnr_inv, error)
        
        return error.item().value
