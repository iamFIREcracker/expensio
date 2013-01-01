#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import env
from fabric.api import require
from fabric.api import run
from fabric.decorators import task

from .utils import cmd


@task
def clone():
    ''' Clone the repository '''
    require('repo_url')
    require('site_path')

    run('hg clone %s %s' % (env.repo_url, env.site_path))

@task
def update():
    ''' Update the repository '''
    cmd('hg pull -u')
