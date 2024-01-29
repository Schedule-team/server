# Schedule-team/server

Django backend to provide api access, basic frontend to display information.

## Setup

*Local:*

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `cp /utils/settings_local.py /api/settings.py`, generate your own secret key
4. `pip install -r requirements.txt`
5. `python manage.py makemigrations` `python manage.py makemigrations course`
6. `python manage.py migrate`
7. `python manage.py createsuperuser`
8. `python manage.py runserver`

*Test Server(`schedule-test.tiankaima.dev`):*

This server is configured to automatically deploy from master branch using docker.

*Production Server(`schedule.tiankaima.dev`):*

Docker image from CI is used as well, a docker-compose file is used to run the server.

1. Stop previous docker container: `docker-compose down`
2. Pull latest image: `docker-compose pull`
3. Start new container: `docker-compose up -d`
