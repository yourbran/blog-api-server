FROM python:3.7.9-slim-buster

WORKDIR /app

COPY main.py .
COPY src ./src
COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["uwsgi", "--ini", "uwsgi.ini"]