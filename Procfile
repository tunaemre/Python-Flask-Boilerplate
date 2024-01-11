release: ./heroku_migration.sh
web: gunicorn --config src/gunicorn_conf.py "src.app:create_app()"
worker-master: celery --app=src.worker worker --beat --queues boilerplate:beat_queue,boilerplate:status_queue,boilerplate:mail_queue --loglevel INFO --without-heartbeat --without-gossip --without-mingle -n worker_master
worker: celery --app=src.worker worker --queues boilerplate:status_queue,boilerplate:mail_queue --loglevel INFO --without-heartbeat --without-gossip --without-mingle -n worker@%%h
