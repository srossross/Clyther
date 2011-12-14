'''
Created on Dec 13, 2011

@author: sean
'''

    
def broadcast_shapes(shapes):
    return reduce(broadcast_shape, shapes)
    
def broadcast_shape(shape1, shape2):
    max_shape = max(shape1, shape2, key=lambda item: (len(item), item))
    min_shape = min(shape1, shape2, key=lambda item: (len(item), item))
    
    ndim = len(max_shape)
    noff = len(max_shape) - len(min_shape)
    
    new_shape = list(max_shape)
    for i in range(noff, ndim):
        if (new_shape[i] == 1) ^ (min_shape[i - noff] == 1):
            new_shape[i] = max(new_shape[i], min_shape[i - noff])
        elif new_shape[i] == min_shape[i - noff]:
            continue
        elif (new_shape[i] != 1) and (min_shape[i - noff] != 1):
            raise ValueError("shape mismatch: objects cannot be broadcast to a single shape")
        
    return tuple(new_shape)
