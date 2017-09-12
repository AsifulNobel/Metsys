from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("stemming_bn.pyx",
    language="c++")
)

# Run command for building c/c++ file from .pyx files:
#   python setup.py build_ext --inplace
