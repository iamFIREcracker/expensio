#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.colors import cyan
from fabric.decorators import task

from . import app
from .config import dev
from . import puppet
from . import virtualenv as venv


@task
def bootstrap():
    ''' Configure the current server '''
    print(cyan("Cloning repo..."))
    app.clone()

    print(cyan("Running puppet..."))
    puppet.apply()

    print(cyan('\nUpdating venv, installing packages...'))
    venv.create()
