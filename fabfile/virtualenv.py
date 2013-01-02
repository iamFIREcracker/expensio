#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.decorators import task

from .utils import sdo
from .utils import vsdo


@task
def create():
    ''' Create app virtualenv '''
    sdo('virtualenv venv --no-site-packages --distribute')

    vsdo('python setup.py install')

@task
def update():
    ''' Update app virtualenv '''
    vsdo('python setup.py install')
