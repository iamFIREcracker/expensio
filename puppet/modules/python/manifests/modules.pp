class python::modules {
  package { [ 'python-dev', ]:
    ensure => 'installed',
  }
  package { [ 'virtualenv', 'virtualenvwrapper' ]:
    ensure => 'installed',
    provider => 'pip',
  }
}
