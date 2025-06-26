#FROM python:3.7-buster Use buster for Matplotlib and tkinter
FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED 1

RUN apt-get update \
  # dependencies for building Python packages
  && apt-get install -y build-essential \
  # psycopg2 dependencies
  && apt-get install -y libpq-dev \
  # Translations dependencies
  && apt-get install -y gettext \
  # install git to install requirements that are only published in GitHub
  && apt-get install -y git \
  && apt-get install -y x11-apps \
  && apt-get install -y python3-tk \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

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
