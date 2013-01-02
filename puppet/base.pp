include gunicorn
include mercurial
include mysql
include nginx
include python
include supervisor
include vagrant

nginx::site {'gunicorn':
  config => 'gunicorn',
}

supervisor::app {'gunicorn':
  config => 'gunicorn',
}
