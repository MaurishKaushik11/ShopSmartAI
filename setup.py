from setuptools import setup, Extension, find_packages
from Cython.Build import cythonize
import numpy

# Define the Cython extension
extensions = [
    Extension(
        "ecommerce.recommendation_engine",
        ["ecommerce/recommendation_engine.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3", "-ffast-math"],
        extra_link_args=["-O3"]
    )
]

setup(
    name="ecommerce_platform",
    packages=['ecommerce'],
    ext_modules=cythonize(extensions, compiler_directives={'language_level': 3}),
    zip_safe=False,
)