FROM python:3.12-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    docker-cli ca-certificates \
    && rm -rf /var/lib/apt/lists/*
COPY requirements /app/requirements
RUN pip install --upgrade pip && pip install -r requirements/base.txt

COPY . /app
CMD ["gunicorn","config.wsgi:application","--bind","0.0.0.0:7712"]