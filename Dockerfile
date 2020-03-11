FROM python:3.7-buster
RUN apt update && apt install -y osmctools
RUN apt install -y postgresql-client
RUN apt install -y pgloader
RUN mkdir /app
WORKDIR /app
ADD requirements.txt .
ADD app.py .
RUN pip3 install -r requirements.txt

