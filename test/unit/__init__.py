# test/unit/__init__.py
#
# Contributing authors (please append):
# Daniel Clark

'''
This package contains subpackages which perform unit testing on all of
C-PAC's various subpackages, modules, and functions
'''

# Import test variables from module
from ..test_variables import *

# Import subpackages
from . import AWS
from . import GUI
from . import network_centrality
from . import pipeline