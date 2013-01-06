include mercurial
include mysql
include nginx
include python
include supervisor

exec { "add_${user}_to_group_www-data":
  path => "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
  command => "usermod -a -G www-data ${user}",
  unless => "id ${user} | grep www-data",
  require => Package[nginx]
}

nginx::site {'gunicorn':
  config => 'gunicorn',
  appname => $appname,
}

supervisor::app {'gunicorn':
  config => 'gunicorn',
  appname => $appname,
  user => $user,
}
