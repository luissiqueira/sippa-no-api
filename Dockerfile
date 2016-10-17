############################################################
# Purpose	: Dockerize Django App to be used in AWS EC2
# Django	: 1.9.7
# OS		: Ubuntu 14.04
# WebServer	: nginx
# Database	: Postgres inside RDS
# Python	: 2.7
# VERSION	: 0.1
############################################################

# take base image from dockerhub
FROM ubuntu:14.04

maintainer Kim Stacks, kimcity@gmail.com

ENV DEBIAN_FRONTEND noninteractive
ENV LIBEV_FLAGS=4

run apt-get upgrade -y
run apt-get update --fix-missing
run apt-get install libssl1.0.0 --force-yes -y

# install python

run apt-get install python	--force-yes -y				## install 2.7
run apt-get install python-setuptools --force-yes -y 	## for python2.7 or above
run apt-get install build-essential --force-yes -y 		##
run apt-get install python-virtualenv --force-yes -y 	## virtual env
run apt-get install python-dev --force-yes -y 		## because ubuntu 14.04 does not have dev version of python 2

## for weasyprint
RUN apt-get install python-lxml libcairo2 libpango1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info --force-yes -y

RUN sudo apt-get install libtiff5-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python-tk --force-yes -y

## postgres dev symbols
RUN apt-get install -y libpq-dev
RUN apt-get install -y libffi-dev
RUN apt-get install -y libssl-dev

# install nginx
run apt-get install \
        nginx \
        --force-yes -y

# install supervisor via apt-get because pip cannot work
RUN apt-get install -y supervisor


########################################
## Install Django
## and associated python modules
########################################
# Install pip
RUN easy_install -U pip

RUN pip install supervisor-stdout

# Add and install Python modules
ADD requirements.txt /src/requirements.txt
RUN cd /src; pip install -r requirements.txt --upgrade


# Bundle app source
# so the folder ./djangoapp inside the host
# gets copied into /src inside the container
ADD . /src

########################################
## Config files here!
########################################

RUN cp /src/deploy/conf/nginx.conf /etc/nginx/

## remove default nginx config
RUN rm /etc/nginx/sites-enabled/default

## symlink the config file so easier to modify
RUN ln -s /src/deploy/conf/django-app.conf	/etc/nginx/sites-enabled/django-app.conf

## symlink supervisor config file
RUN ln -s /src/deploy/conf/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

run mkdir /var/log/newrelic
run mkdir /var/run/newrelic

## run djangostuff such as migrations and set up static
ONBUILD RUN cd /src && python manage.py migrate --noinput


# Expose container port to host
EXPOSE 80

# supervisord == python program
# used to keep linux packages or commands running

########################################
## Remove any unwanted packages
########################################
run apt-get autoremove --force-yes -y

## default command when you startup
CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]