class mysql {
  package { [ 'mysql-server', 'libmysqlclient-dev' ]:
    ensure => 'installed',
  }
  service { 'mysql':
    ensure => running,
    require => Package['mysql-server']
  }
}
