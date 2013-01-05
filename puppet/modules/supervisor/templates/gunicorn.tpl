[program:expenses]
autostart=true
autorestart=true
directory=/srv/www/expenses
user=www-data
group=www-data
command=/srv/www/expenses/venv/bin/gunicorn -c /srv/www/expenses/gunicorn.conf.py app:app
