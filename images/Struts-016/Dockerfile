FROM tomcat:8-jre8
MAINTAINER vulfocus@bmh.com

ENV WAR_URL https://github.com/sie504/Struts-S2-xxx/raw/master/s2-016.war

WORKDIR /tmp

RUN set -ex \
    && rm -rf /usr/local/tomcat/webapps/* \
    && chmod a+x /usr/local/tomcat/bin/*.sh \
    && wget -qO /usr/local/tomcat/webapps/ROOT.war $WAR_URL

EXPOSE 8080
CMD ["/usr/local/tomcat/bin/catalina.sh", "run"]