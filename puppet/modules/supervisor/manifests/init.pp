class supervisor {
  package { 'supervisor':
    ensure => installed,
  }
  service { 'supervisor':
    ensure => running,
  }
}

define supervisor::app( $config, $user ) {
  file { "/etc/supervisor/conf.d/${config}.conf":
    ensure  => present,
    owner   => root,
    group   => root,
    mode    => '644',
    content => template("supervisor/${config}.tpl"),
    require => Package[supervisor],
    notify  => Service[supervisor],
  }
}

