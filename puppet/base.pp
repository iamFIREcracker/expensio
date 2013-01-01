include gunicorn
include mercurial
include mysql
include nginx
include python
include vagrant

nginx::site {'gunicorn':
  config => 'gunicorn',
}
