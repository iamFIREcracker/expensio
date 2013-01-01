#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.decorators import task

from .utils import cmd
from .utils import vcmd


@task
def create():
    ''' Create app virtualenv '''
    cmd('virtualenv venv --distribute')

    vcmd('python setup.py install')

@task
def update():
    ''' Update app virtualenv '''
    vcmd('python setup.py install')
