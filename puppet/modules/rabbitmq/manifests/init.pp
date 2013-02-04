class rabbitmq {
  package { [ 'rabbitmq-server' ]:
    ensure => 'installed',
  }
  service { 'rabbitmq-server':
    ensure => running,
    require => Package['rabbitmq-server']
  }
}

define rabbitmq::connection( $user, $password, $vhost ) {
  exec { 'rabbitmq-user':
    require => Package[ 'rabbitmq-server' ],
    command => "rabbitmqctl add_user $user $password",
    unless  => "rabbitmqctl list_users | grep $user",
  } -> 
  exec { 'rabbitmq-user-permissions':
    command => "rabbitmqctl set_permissions -p $vhost $user '.*' '.*' '.*'",
    unless  => "rabbitmqctl list_user_permissions $user | grep $vhost",
    notify => Service[ 'rabbitmq-server' ],
  }
}
