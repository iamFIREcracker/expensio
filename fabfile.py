#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

from fabric.api import hide
from fabric.api import cd
from fabric.api import env
from fabric.api import local
from fabric.api import run
from fabric.api import require
from fabric.api import settings
from fabric.api import sudo
from fabric.colors import cyan
from fabric.colors import green
from fabric.colors import red
from fabric.decorators import task


env.repo_url = 'https://iamFIREcracker@bitbucket.org/iamFIREcracker/expenses'


def vagrant_key():
    ''' Get the ssh key to access the virtual box machine. '''
    with settings(hide('running')):
        result = local('vagrant ssh-config | grep IdentityFile', capture=True)
    return result.split()[1]


@task
def dev():
    ''' Use virtual machine settings. '''
    env.user = 'vagrant'
    env.hosts = ['127.0.0.1:2222']
    env.key_filename = vagrant_key()

    env.site_path = '/srv/www/expenses'
    env.venv_path = '/srv/www/expenses/venv'
    env.site_url  = 'http://expenses.matteolandi.net:9090'

    env.skip_repo = True



def _happy():
    print(green('\nLooks good from here!\n'))


def _sad():
    print(red(r'''
          ___           ___
         /  /\         /__/\
        /  /::\        \  \:\
       /  /:/\:\        \__\:\
      /  /:/  \:\   ___ /  /::\
     /__/:/ \__\:\ /__/\  /:/\:\
     \  \:\ /  /:/ \  \:\/:/__\/
      \  \:\  /:/   \  \::/
       \  \:\/:/     \  \:\
        \  \::/       \  \:\
         \__\/         \__\/
          ___           ___           ___           ___
         /__/\         /  /\         /  /\         /  /\     ___
         \  \:\       /  /::\       /  /:/_       /  /:/_   /__/\
          \  \:\     /  /:/\:\     /  /:/ /\     /  /:/ /\  \  \:\
      _____\__\:\   /  /:/  \:\   /  /:/ /:/_   /  /:/ /::\  \  \:\
     /__/::::::::\ /__/:/ \__\:\ /__/:/ /:/ /\ /__/:/ /:/\:\  \  \:\
     \  \:\~~\~~\/ \  \:\ /  /:/ \  \:\/:/ /:/ \  \:\/:/~/:/   \  \:\
      \  \:\  ~~~   \  \:\  /:/   \  \::/ /:/   \  \::/ /:/     \__\/
       \  \:\        \  \:\/:/     \  \:\/:/     \__\/ /:/          __
        \  \:\        \  \::/       \  \::/        /__/:/          /__/\
         \__\/         \__\/         \__\/         \__\/           \__\/

         Something seems to have gone wrong!
         You should probably take a look at that.
    '''))


@task
def cmd(cmd=""):
    '''Run a command in the site directory.  Usable from other commands or the CLI.'''
    require('site_path')

    if not cmd:
        sys.stdout.write(cyan("Command to run: "))
        cmd = raw_input().strip()

    if cmd:
        with cd(env.site_path):
            run(cmd)


@task
def sdo(cmd=""):
    '''Sudo a command in the site directory.  Usable from other commands or the CLI.'''
    require('site_path')

    if not cmd:
        sys.stdout.write(cyan("Command to run: sudo "))
        cmd = raw_input().strip()

    if cmd:
        with cd(env.site_path):
            sudo(cmd)


@task
def dbupdate():
    '''Update the database schema.'''
    vcmd('alembic upgrade head')


@task
def papply():
    '''Apply Puppet manifest. Usable from other commands or the CLI.'''
    require('user')

    sdo('FACTER_APPNAME=expenses FACTER_USER=%s puppet apply --modulepath=puppet/modules/ puppet/base.pp' % env.user)


@task
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


@task
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


@task
def vcreate():
    '''Create the virtualenv.  Usable from other commands or the CLI.'''
    require('venv_path')

    run('mkdir -p %s' % env.venv_path)
    run('virtualenv %s --no-site-packages --distribute' % env.venv_path)

    vupdate()


@task
def vupdate():
    '''Update the virtualenv.  Usable from other commands or from the CLI.'''
    vcmd('python setup.py install')


@task
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


@task
def rclone():
    ''' Clone the app repository repository. '''
    require('repo_url')
    require('site_path')

    run('mkdir -p %s' % env.site_path)
    run('hg clone %s %s' % (env.repo_url, env.site_path))


@task
def rupdate():
    ''' Update the repository. '''

    cmd('hg pull -u')


@task
def rtag():
    '''Check which revision the site is at and update the local tag.

    Useful if someone else has deployed (which makes your production/staging local
    tag incorrect.
    '''
    require('site_path', provided_by=['prod', 'stag'])
    require('env_name', provided_by=['prod', 'stag'])

    with cd(env.site_path):
        current = run('hg id --rev . --quiet').strip(' \n+')

    local('hg tag --local --force %s --rev %s' % (env.env_name, current))




@task
def bootstrap():
    ''' Configure the app '''
    if 'skip_repo' not in env:
        print(cyan("Cloning repo..."))
        rclone()

    print(cyan("Applying puppet manifest..."))
    papply()

    print(cyan('Creating venv...'))
    vcreate()

    print(cyan('Initialize database...'))
    dbupdate()


@task
def update():
    ''' Update everything related to the app. '''
    if 'skip_repo' not in env:
        print(cyan("Cloning repo..."))
        rupdate()

    print(cyan("Applying puppet manifest..."))
    papply()

    print(cyan('Updating venv...'))
    vupdate()

    print(cyan('Updating database...'))
    dbupdate()

    restart()


@task
def restart():
    ''' Restart the app.  Usable from other commands or from the CLI.'''
    print(cyan("Restarting gunicorn..."))
    cmd("sudo supervisorctl restart expenses")
