[program:celery]
command=/srv/www/<%= @appname %>/venv/bin/celery --app=app --loglevel=info --logfile=celery.log
directory=/srv/www/<%= @appname %>
user=<%= @user %>
group=<%= @user %>
autostart=true
autorestart=true
redirect_stderr=True
