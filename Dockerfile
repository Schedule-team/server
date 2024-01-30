FROM python:3.11
RUN apt-get update && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade -r requirements.txt
COPY . /app/
COPY /app/utils/settings_docker.py /app/settings.py

# use gunicorn
CMD ["python", "-m", "gunicorn", "api.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]