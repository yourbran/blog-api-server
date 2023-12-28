# Flask API Dockerfile
FROM python:3.7

WORKDIR /flaskapi

COPY main.py /flaskapi
COPY uwsgi.ini /flaskapi
COPY appConfig.ini /flaskapi
COPY requirements.txt /flaskapi
COPY common/ /flaskapi/common/
COPY searchaddr/ /flaskapi/searchaddr/

# chrome setting for scraping
COPY chrome_114_amd64.deb /flaskapi/
RUN  mkdir chromedriver
ADD  chromedriver_114.tar /flaskapi/chromedriver/
RUN  apt-get -y update && apt -y install ./chrome_114_amd64.deb && rm chrome_114_amd64.deb 

# ls project tree
# RUN ls --recursive /flaskapi/

# Install Flask, uWSGI, etc..
RUN python -m pip install --upgrade pip 
RUN pip3 install -r requirements.txt

# Create account
RUN  groupadd -g 1000 ec2-user && useradd -r -u 1000 -g ec2-user ec2-user
USER ec2-user

# Directory for UNIX socket connection between container and host
VOLUME /flaskapi/socket

# Directory for FlaskAPI log
VOLUME /flaskapi/logs

ENTRYPOINT ["uwsgi", "--ini", "uwsgi.ini"]