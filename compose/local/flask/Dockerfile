#FROM python:3.7-buster Use buster for Matplotlib and tkinter
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
  && apt-get install -y x11-apps \
  && apt-get install -y python3-tk \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*


RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

WORKDIR /app

# Requirements are installed here to ensure they will be cached.
COPY requirements/ requirements
COPY api/server api/server
RUN pip install cmake \
  && pip install cython
RUN pip install --upgrade pip  \
  && pip install -r requirements/deploy.txt

COPY ./compose/production/flask/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint


COPY ./compose/local/flask/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

ENTRYPOINT ["/entrypoint"]
