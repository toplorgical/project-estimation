# pull official base image
FROM python:3.11.4-slim-buster

# set work directory
WORKDIR /usr/src/app/server

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update && apt-get install -y netcat

RUN pip install --upgrade pip
RUN pip install flake8==6.0.0
COPY . /usr/src/app/server
# RUN flake8 --ignore=E501,F401 .

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]