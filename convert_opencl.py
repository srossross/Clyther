'''
'''
from cwrap.config import Config, File
from glob import glob
from argparse import ArgumentParser
from os.path import join, exists, abspath
if __name__ == '__main__':
    
    
    
    parser = ArgumentParser(description=__doc__)
    mac_frameworks = ['/System/Library/Frameworks/'] + glob('/Developer/SDKs/MacOSX*.sdk/System/Library/Frameworks')
    parser.add_argument('-F', action='append', dest='framework_paths', default=mac_frameworks)
    parser.add_argument('--framework', action='append', dest='frameworks', default=[])
    
    parser.add_argument('-I', action='append', dest='include_dirs', default=[])
    parser.add_argument('-i', '--header', action='append', dest='headers', default=[])
    parser.add_argument('-o', dest='output_dir', required=True)
     
    args = parser.parse_args()
    
    print args.framework_paths
    print args.frameworks
    
    for framework in args.frameworks:
        for fdir in args.framework_paths:
            path = join(abspath(fdir), framework + '.framework')
            if exists(path):
                args.include_dirs.append(path + '/Versions/Current/Headers/')
                break
        else:
            raise Exception("could not find framework %s" % (framework))
        
    headers = []
    for header in args.headers:
        for include in args.include_dirs:
            path = join(abspath(include), header)
            print "path", path
            if exists(path):
                headers.append(path)
                break
        else:
            raise Exception("could not find header %s" % (header))
            
    
    config = Config('gccxml', save_dir=args.output_dir, files=[File(header) for header in headers])
    config.generate()
