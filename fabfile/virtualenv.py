#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import env
from fabric.api import require
from fabric.api import run
from fabric.decorators import task

from .utils import vcmd


@task
def create():
    ''' Create app virtualenv '''
    require('venv_path')

    run('mkdir -p %s' % env.venv_path)
    run('virtualenv %s --no-site-packages --distribute' % env.venv_path)

    vcmd('python setup.py install')

@task
def update():
    ''' Update app virtualenv '''
    vcmd('python setup.py install')
