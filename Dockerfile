FROM centos:7
MAINTAINER Brayan Quiñones
RUN yum install -y net-tools vim git epel-release python3-pip tree mod_wsgi mysql-devel python3-devel gcc httpd
COPY requirements.txt /tmp/
RUN pip3 install -r /tmp/requirements.txt
COPY . /tmp/
RUN git clone https://github.com/groloboy/Flask_test.git html
RUN yes | cp -r html/ /var/www/html/
RUN chmod -R 777 /var/www/html
RUN yes | cp -r html/httpd.conf /etc/httpd/conf/httpd.conf
EXPOSE 80
CMD ["/usr/sbin/httpd", "-D", "FOREGROUND"]