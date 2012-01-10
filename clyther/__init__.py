'''
clyther
---------------------------


'''

from __future__ import print_function

from cly_kernel import kernel, global_work_size, local_work_size, developer, task, cache

from clyther.queue_record import QueueRecord
import sys

def test(stream=sys.stdout, descriptions=True, verbosity=2, failfast=False, buffer=False):
    '''
    Load and run the clyther test suite.
    '''
    import unittest as _unit
    import os as _os
    star_dir = _os.path.dirname(__file__)
    test_suite = _unit.defaultTestLoader.discover(star_dir)
    runner = _unit.TextTestRunner(stream, descriptions, verbosity, failfast, buffer)
    runner.run(test_suite)

from .version import __version__
 