#!/usr/bin/env python
# -*- coding: utf-8 -*-

from fabric.api import env
from fabric.api import hide
from fabric.api import local
from fabric.api import settings
from fabric.decorators import task


env.repo_url = 'https://iamFIREcracker@bitbucket.org/iamFIREcracker/expenses'

def vagrant_key():
    """ Get the ssh key to access the virtual box machine """
    with settings(hide('stdout')):
        result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    return result.split()[1]

@task
def dev():
    """ Use virtual machine settings. """
    env.hosts = ['vagrant@127.0.0.1:2222']
    env.key_filename = vagrant_key()

    env.site_path = '/srv/www/expenses'
    env.venv_path = '/srv/www/expenses/venv'
    env.site_url  = 'http://expenses.matteolandi.net:9090'
    env.env_name  = 'dev'
