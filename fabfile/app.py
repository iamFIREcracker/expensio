#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import env
from fabric.api import require
from fabric.api import run
from fabric.decorators import task

from .utils import cmd


@task
def clone():
    ''' Clone the app repository repository '''
    require('repo_url')
    require('site_path')
    require('env_name')

    if 'skip_clone' not in env:
        run('mkdir -p %s' % env.site_path)
        run('hg clone %s %s' % (env.repo_url, env.site_path))


@task
def update():
    ''' Update the repository '''
    cmd('hg pull -u')
