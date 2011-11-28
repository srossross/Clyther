from clyther.disasembler import ast_from_function, expression_from_ast, printDis, \
    code_from_ast
import dis
import inspect
import compiler



def test_deco(func, args):
    
    astnodes = ast_from_function(func)

    new_func = expression_from_ast(astnodes, func)
    
    result = new_func(*args)
    expected = func(*args)
    if not result == expected:
#        raise Exception("%r != %r" % (result , expected))
        print "FAIL: %r != %r" % (result , expected)
    else:
        print "PASS: %r == %r" % (result , expected)
    
    
def foo(x,y):
    
    while x and y:
        x-=1
        y+=1
        
    return x,y

def bar1(x):
    
    try:
        x = i
    except Exception as e:
        x=0
    else:
        print 
    finally:
        x+=1
        
def bar(z):
    
    while True:
        if x > 1:
            d = True
            
    return

def main():

    print 
    print bar 
    dis.dis(bar)
    
    print compiler.parse(inspect.getsource(bar))
    print 
    node = ast_from_function(bar)
    
    print 
    print "node",node
    print 
    code_from_ast(node)
if __name__ == '__main__':
    
    main()
    
    
