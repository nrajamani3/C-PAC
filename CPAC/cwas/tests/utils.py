import inspect, os
from os import path as op

def path_to_directory():
    return op.dirname(op.abspath(inspect.getfile(inspect.currentframe())))

def path_to_data(fname):
    fpath = op.join(path_to_directory(), "data", fname)
    if not op.exists(fpath):
        raise Exception("Could not locate the test data: %s" % fpath)
    return fpath
