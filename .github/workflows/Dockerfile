FROM python:3.7-slim-buster

RUN apt-get update \
    # dependencies for building Python packages
    && apt-get install -y build-essential git

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
RUN pip install --upgrade pip
RUN pip install -r /requirements/ci.txt

ENTRYPOINT [ "python3" ]
