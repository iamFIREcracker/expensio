#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.decorators import task

from .app import clone, update
from .config import *
from .puppet import *
from .utils import *
from .virtualenv import create as vcreate


@task
def bootstrap():
    ''' Configure the current server '''
    print(cyan("Running puppet..."))
    apply()


    print(cyan("Cloning repo..."))
    clone()

    print(cyan('\nUpdating venv, installing packages...'))
    vcreate()
