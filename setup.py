from distutils.core import setup
from setuptools import find_packages
from os import path
import pkg_resources  # part of setuptools

__version__ = "0.2.1"
setup(
    name='CancerUtils',
    version=__version__,
    packages=find_packages(),
    package_data={'CancerUtils': ['resources/*']},
    license='GNU General Public License v3.0',
    author='Matthew Davis',
    author_email='davismat@musc.edu',
    description='a package of utilities for work with cancer EHR data',
    zip_safe=True
)
