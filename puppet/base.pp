include mercurial
include mysql
include nginx
include python
include rabbitmq
include supervisor

Exec {
  path => [ "/usr/local/sbin", "/usr/local/bin", "/usr/sbin", "/usr/bin", "/sbin", "/bin", ],
}

exec { "add_${user}_to_group_www-data":
  command => "usermod -a -G www-data ${user}",
  unless => "id ${user} | grep www-data",
  require => Package[nginx]
}

nginx::site {'gunicorn':
  config => 'gunicorn',
  appname => $appname,
}

supervisor::app {'supervisor-gunicorn':
  appname => $appname,
  user => $user,
}

supervisor::celery {'supervisor-celery':
  appname => $appname,
  user => $user,
}

rabbitmq::connection {'rabbitmq':
  user => 'expenses',
  password => 'expenses',
  vhost => '/',
}
