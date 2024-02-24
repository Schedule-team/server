# Schedule-team/server

Django backend to provide api access, basic frontend to display information.

## Setup

### *Local:*

1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `cp ./utils/settings_local.py ./api/settings.py`, generate your own secret key
4. `pip install -r requirements.txt`
5. `python manage.py migrate`
6. `python manage.py createsuperuser`
7. `python manage.py runserver`

### *Test Server(`schedule-test.tiankaima.dev`):*

This server is configured to automatically deploy from master branch using docker.

### *Production Server(`schedule.tiankaima.dev`):*

Uses docker as well but requires manual update.

#### Installation

1. Clone repo: `git clone git@github.com:Schedule-team/server.git`
2. `cd server`
3. `docker-compose up -d`
4. `docker-compose exec schedule /bin/bash`
5. `python manage.py migrate`
6. `python manage.py createsuperuser`
7. `python manage.py collectstatic`

An example `Caddyfile` is provided in `utils/Caddyfile`, static files are served through gunicorn not caddy, you can
manually configure caddy to serve static files if you want.

#### Update

1. Stop previous docker container: `docker-compose down`
2. Pull latest image: `docker-compose pull`
3. Start new container: `docker-compose up -d`
