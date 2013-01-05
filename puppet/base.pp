include mercurial
include mysql
include nginx
include python
include supervisor

nginx::site {'gunicorn':
  config => 'gunicorn',
}

supervisor::app {'gunicorn':
  config => 'gunicorn',
}
