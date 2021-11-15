.PHONY: start stop install install_and_run test coverage

start:
	docker-compose up -d

stop:
	docker-compose down

install:
	docker-compose build
	docker-compose up -d
	docker-compose exec django-ml python manage.py migrate --noinput
	docker-compose exec django-ml python manage.py createsuperuser --noinput
	docker-compose down

install_and_run:
	docker-compose build
	docker-compose up -d
	docker-compose exec django-ml python manage.py migrate --noinput
	docker-compose exec django-ml python manage.py createsuperuser --noinput

test:
	docker-compose exec django-ml python manage.py test

coverage:
	docker-compose exec django-ml pip install coverage
	docker-compose exec django-ml coverage run manage.py test
	docker-compose exec django-ml coverage html
