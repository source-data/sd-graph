FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED 1
ENV DOCKERIZE_VERSION v0.6.1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # Dockerize dependency
  && apt-get install -y openssl wget \
  # install git to install requirements that are only published in GitHub
  && apt-get install -y git \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN addgroup --system flask \
    && adduser --system --ingroup flask flask

RUN pip install cmake \
  && pip install cython

WORKDIR /app

# Requirements are installed here to ensure they will be cached.
COPY requirements/ /requirements
COPY api/server api/server
RUN pip install --upgrade pip  \
    pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

COPY ./compose/production/flask/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint
RUN chown flask /entrypoint

COPY ./compose/production/flask/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
RUN chown flask /start

COPY --chown=flask:flask . /app
# make sure the log dir is owned by flask
RUN mkdir -p /app/log
RUN chown flask:flask /app/log

USER flask

ENTRYPOINT ["/entrypoint"]
