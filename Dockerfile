FROM centos
MAINTAINER Brayan Quiñones
RUN yum install -y httpd
RUN yum install -y epel-release
RUN yum install python-pip -y -y
RUN pip install Flask
RUN yum install mod_wsgi -y
RUN yum install mysql-devel -y
RUN yum install gcc gcc-c++ kernel-devel -y
RUN yum install python-devel libxsly-devel libffi-devel openssl-devel -y
RUN pip install flask-mysqldb
RUN pip install Flask-WTF
RUN pip install passlib
RUN yum install python-devel -y

#RUN git clone https://github.com/groloboy/Flask_test.git html
COPY project/ /var/www/project
COPY project/httpd.conf /etc/httpd/conf
RUN chmod -R 777 /var/www/project

ENV FLASK_APP=run.py
ENV FLASK_ENV=development

EXPOSE 80
CMD ["/usr/sbin/httpd", "-D", "FOREGROUND"]