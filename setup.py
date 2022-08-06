# -*- coding: utf-8 -*-

from setuptools import find_packages
from distutils.core import setup

setup(
      name='sapai',
      version='0.1.0',
      packages=['sapai',
                ],
      #find_packages(exclude=[]),
      install_requires=['numpy', 'keras','torch', 'graphviz'],
      data_files=[],
      )
