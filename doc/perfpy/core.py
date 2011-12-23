'''
Created on Dec 22, 2011

@author: sean
'''

class Grid(object):
    
    """A simple grid class that stores the details and solution of the
    computational grid."""
    
    def __init__(self, np, nx=10, ny=10, xmin=0.0, xmax=1.0,
                 ymin=0.0, ymax=1.0):
        self.np = np
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax
        self.dx = float(xmax - xmin) / (nx - 1)
        self.dy = float(ymax - ymin) / (ny - 1)
        self.u = np.zeros((nx, ny), 'f')
        # used to compute the change in solution in some of the methods.
        self.old_u = self.u.copy()        

    def setBC(self, l, r, b, t):        
        """Sets the boundary condition given the left, right, bottom
        and top values (or arrays)"""        
        self.u[0, :] = l
        self.u[-1, :] = r
        self.u[:, 0] = b
        self.u[:, -1] = t
        self.old_u = self.u.copy()

    def setBCFunc(self, func):
        """Sets the BC given a function of two variables."""
        xmin, ymin = self.xmin, self.ymin
        xmax, ymax = self.xmax, self.ymax
        x = self.np.arange(xmin, xmax + self.dx * 0.5, self.dx)
        y = self.np.arange(ymin, ymax + self.dy * 0.5, self.dy)
        self.u[0 , :] = func(xmin, y)
        self.u[-1, :] = func(xmax, y)
        self.u[:, 0] = func(x, ymin)
        self.u[:, -1] = func(x, ymax)

    def computeError(self):        
        """Computes absolute error using an L2 norm for the solution.
        This requires that self.u and self.old_u must be appropriately
        setup."""        
        v = (self.u - self.old_u).flat
        return self.np.sqrt(self.np.dot(v, v))

    
class TimeSteper(object):
    @classmethod
    def create_grid(cls, nx=500, ny=500):
        import numpy as np
        g = Grid(np, nx, ny)
        return g

    @classmethod
    def finish(cls, grid):
        pass


timestep_methods = {}
 
get_title = lambda func: func.__doc__.splitlines()[0].strip()

def available(test):
    def decorator(func):
        func.available = bool(test)
        timestep_methods[get_title(func)] = func
        return func
    
    return decorator
