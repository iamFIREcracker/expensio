[program:expenses]
command=/srv/www/expenses/venv/bin/gunicorn -c /srv/www/expenses/gunicorn.conf.py app:app
directory=/srv/www/expenses
user=<%= @user %>
group=<%= @user %>
autostart=true
autorestart=true
redirect_stderr=True
