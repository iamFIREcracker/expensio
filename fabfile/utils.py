#!/usr/bin/env python

import sys

from fabric.api import cd
from fabric.api import env
from fabric.api import local
from fabric.api import run
from fabric.api import require
from fabric.api import settings
from fabric.api import sudo
from fabric.colors import cyan

from status import _happy, _sad


def vagrant():
    """ Use virtual machine settings. """
    def vagrant_key():
        result = local('vagrant ssh-config | grep IdentityFile', capture=True)
        return result.split()[1]

    env.hosts = ['vagrant@127.0.0.1:2222']
    env.key_filename = vagrant_key()

    env.site_path = '/vagrant'
    env.venv_path = '~/.virtualenvs/expenses'
    env.site_url  = 'http://expenses.matteolandi.net:9090'
    env.env_name  = 'vagrant'


def dev():
    """ Use development server settings."""
    vagrant();


def stag():
    env.hosts = ['expenses.matteolandi.net']

    env.site_path = '/vagrant'
    env.venv_path = '~/.virtualenvs/expenses'
    env.site_url  = 'http://expenses.matteolandi.net'
    env.env_name  = 'vagrant'


def prod():
    pass


def cmd(cmd=""):
    '''Run a command in the site directory.  Usable from other commands or the CLI.'''
    require('site_path')

    if not cmd:
        sys.stdout.write(cyan("Command to run: "))
        cmd = raw_input().strip()

    if cmd:
        with cd(env.site_path):
            run(cmd)


def sdo(cmd=""):
    '''Sudo a command in the site directory.  Usable from other commands or the CLI.'''
    require('site_path')

    if not cmd:
        sys.stdout.write(cyan("Command to run: sudo "))
        cmd = raw_input().strip()

    if cmd:
        with cd(env.site_path):
            sudo(cmd)

def vcmd(cmd=""):
    '''Run a virtualenv-based command in the site directory.  Usable from other commands or the CLI.'''
    require('site_path')
    require('venv_path')

    if not cmd:
        sys.stdout.write(cyan("Command to run: %s/bin/" % env.venv_path.rstrip('/')))
        cmd = raw_input().strip()

    if cmd:
        with cd(env.site_path):
            run(env.venv_path.rstrip('/') + '/bin/' + cmd)

def vsdo(cmd=""):
    '''Sudo a virtualenv-based command in the site directory.  Usable from other commands or the CLI.'''
    require('site_path')
    require('venv_path')

    if not cmd:
        sys.stdout.write(cyan("Command to run: sudo %s/bin/" % env.venv_path.rstrip('/')))
        cmd = raw_input().strip()

    if cmd:
        with cd(env.site_path):
            sudo(env.venv_path.rstrip('/') + '/bin/' + cmd)

def check():
    '''Check that the home page of the site returns an HTTP 200.'''
    require('site_url')

    print('Checking site status...')

    with settings(warn_only=True):
        result = local('curl --silent -I "%s"' % env.site_url, capture=True)
    if not '200 OK' in result:
        _sad()
    else:
        _happy()

def retag():
    '''Check which revision the site is at and update the local tag.

    Useful if someone else has deployed (which makes your production/staging local
    tag incorrect.
    '''
    require('site_path', provided_by=['prod', 'stag'])
    require('env_name', provided_by=['prod', 'stag'])

    with cd(env.site_path):
        current = run('hg id --rev . --quiet').strip(' \n+')

    local('hg tag --local --force %s --rev %s' % (env.env_name, current))
