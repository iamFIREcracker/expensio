#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.decorators import task

from .utils import cmd


@task
def apply():
    ''' Apply Puppet manifest. '''
    cmd('sudo puppet apply --modulepath=puppet/modules/ puppet/base.pp')
