uwsgi --socket server.sock --wsgi-file server.py --callable app --chmod-socket=666 --daemonize server-web-ppsay.log --catch-exceptions
