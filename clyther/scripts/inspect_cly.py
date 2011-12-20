'''
Created on Dec 20, 2011

@author: sean
'''
from argparse import ArgumentParser
import h5py
import pickle
from clyther.rttt import str_type
import opencl as cl



def create_parser():
    parser = ArgumentParser(description=__doc__)
    
    parser.add_argument('input')
    parser.add_argument('-f', '--functions', action='store_true')
    parser.add_argument('-s', '--short', action='store_true')
    return parser

def main():
    
    parser = create_parser()
    
    args = parser.parse_args()

    hf = h5py.File(args.input, 'r')
    
    
    for funcname in hf.keys():
        print "Kernel Function: '%s'" % (funcname,)
        
        func = hf[funcname]
        
        groups = {}
        for func_code_group in func.values():
            for arg_group in func_code_group.values():
                
                items = pickle.loads(arg_group.attrs['args'])
                
                if args.short:
                    argstr = ', '.join('%s' % str_type(item[1], {}) for item in items)
                else:
                    argstr = ', '.join('%s %s' % (str_type(item[1], {}), item[0]) for item in items)
                    
                name = arg_group.attrs['kernel_name']
                meta = arg_group.attrs['meta']
                
                if args.short:
                    defn = '%s(%s)' % (name, argstr)
                else:
                    defn = '__kernel void %s(%s);' % (name, argstr)

                groups.setdefault(meta, []).append(defn)
                
        for meta, kernels in groups.items():
            print "   + %s" % (meta,)
            for kernel in kernels:
                print "     - %s" % (kernel,)
                 
              
        
        

if __name__ == '__main__':
    main()
