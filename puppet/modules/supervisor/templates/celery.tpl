[program:celery]
command=/srv/www/<%= @appname %>/venv/bin/celery --config /srv/www/<%= @appname %>/celeryconfig.py 
directory=/srv/www/<%= @appname %>
user=<%= @user %>
group=<%= @user %>
autostart=true
autorestart=true
redirect_stderr=True
