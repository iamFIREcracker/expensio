[program:expenses]
autostart=true
autorestart=true
directory=/srv/www/expenses
#user=www-data
#group=www-data
command=/srv/www/expenses/venv/bin/gunicorn --workers 4 --log-file /srv/www/expenses/gunicorn.log expenses:app
