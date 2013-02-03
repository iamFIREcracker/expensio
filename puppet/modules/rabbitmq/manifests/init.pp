class rabbitmq {
  package { [ 'rabbitmq-server' ]:
    ensure => 'installed',
  }
  service { 'rabbitmq':
    ensure => running,
    require => Package['rabbitmq-server']
  }
}

