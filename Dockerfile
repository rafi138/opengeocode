FROM python:3.7-buster
RUN apt update && apt install -y osmctools
RUN mkdir /app
WORKDIR /app
ADD requirements.txt .
ADD app.py .
RUN pip3 install -r requirements.txt
CMD ["/usr/local/bin/gunicorn", "--worker-class=gevent", "--worker-connections=1000", "--bind", "0.0.0.0:5555", "app:app", "--workers=4", "-t", "60"]

