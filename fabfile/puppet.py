#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.decorators import task

from .utils import sdo


@task
def apply():
    ''' Apply Puppet manifest. '''
    sdo('puppet apply --modulepath=puppet/modules/ puppet/base.pp')
