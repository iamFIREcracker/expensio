#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from setuptools import find_packages
from setuptools import setup


NAME = 'expenses'
VERSION = '0.0.1'
requirements = os.path.join(os.path.dirname(__file__), 'requirements.txt')
INSTALL_REQUIRES = open(requirements).read().split()


params = dict(
    name=NAME,
    version=VERSION,
    packages=find_packages(exclude=['fabfile']),
    install_requires=INSTALL_REQUIRES,
)

setup(**params)
