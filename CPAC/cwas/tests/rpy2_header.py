import numpy as np
import rpy2.robjects as robjects
from rpy2.robjects.numpy2ri import numpy2ri
from rpy2.robjects.packages import importr
robjects.conversion.py2ri = numpy2ri
#numpy2ri.activate()
