#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import env
from fabric.api import require
from fabric.decorators import task

from .utils import sdo


@task
def apply():
    ''' Apply Puppet manifest. '''
    require('user')

    sdo('FACTER_USER=%s puppet apply --modulepath=puppet/modules/ puppet/base.pp' % env.user)
