Vulfocus 镜像维护目录，该目录中存储 Vulfocus 所有的 Dockerfile 信息，提交者需在此文件夹中创建漏洞对应的环境目录，然后在此目录中编译 Dockerfile 文件，最后将漏洞镜像信息提交至该文件中。

| id   | 漏洞名称         | 镜像名称                                             | 描述             |
| :--- | :--------------- | :--------------------------------------------------- | :--------------- |
| 1    | CVE-2019-12409   | `docker pull vulfocus/solr-cve_2019_12409`           | CVE-2019-12409   |
| 2    | CVE-2020_10238、CVE-2020-10239、CVE-2020-11890  | `vulfocus/joomla-cve_2020_10238_10239_11890`           | CVE-2020_10238、CVE-2020-10239、CVE-2020-11890   |
| 3    | CVE-2020-7961    | `docker pull vulfocus/liferay-cve_2020_7961`         | CVE-2020-7961    |
| 4    | CVE-2020-2883    | `docker pull vulfocus/weblogic-cve_2020_2883`          | CVE-2020-2883    |
| 5    | CVE-2020-2555    | `docker pull vulfocus/weblogic-cve_2020_2555`          | CVE-2020-2555    |
| 6    | CVE-2020-2551    | `docker pull vulfocus/weblogic-cve_2020_2551`          | CVE-2020-2551    |
| 7    | CVE-2020-1938    | `docker pull vulfocus/tomcat-cve_2020_1938`          | CVE-2020-1938    |
| 8    | CNVD-2019-22238  | `docker pull vulfocus/fastjson-cnvd_2019_22238`      | CNVD-2019-22238  |
| 9    | CVE-2019-17564   | `docker pull vulfocus/dubbo-cve_2019_17564`          | CVE-2019-17564   |
| 10   | CVE-2019-15107   | `docker pull vulfocus/webmin-cve_2019_15107`         | CVE-2019-15107   |
| 11   | CVE-2019-8942    | `docker pull vulfocus/wordpress-cve_2019_8942`       | CVE-2019-8942    |
| 12   | CNVD-2018-24942  | `docker pull vulfocus/thinkphp-cnvd_2018_24942`      | CNVD-2018-24942  |
| 13   | CVE-2018_1000861 | `docker pull vulfocus/jenkins-cve2018_1000861`       | CVE-2018_1000861 |
| 14   | CVE-2018-7600    | `docker pull vulfocus/drupal-cve_2018_7600`          | CVE-2018-7600    |
| 15   | CVE-2017_1000353 | `docker pull vulfocus/jenkins-cve2017_1000353`       | CVE-2017_1000353 |
| 16   | CVE-2017-12636   | `docker pull vulfocus/couchdb-cve_2017_12636`        | CVE-2017-12636   |
| 17   | CVE-2017-12615   | `docker pull vulfocus/tomcat-cve_2017_12615`         | CVE-2017-12615   |
| 18   | CVE-2017-12149   | `docker pull vulfocus/jboss-cve_2017_12149`          | CVE-2017-12149   |
| 19   | CVE-2017-9791    | `docker pull vulfocus/struts2-cve_2017_9791`         | CVE-2017-9791    |
| 20   | CVE-2017_8046    | `docker pull vulfocus/vulfocus/spring-cve_2017_8046` | CVE-2017_8046    |
| 21   | CVE-2017-7504    | `docker pull vulfocus/jboss-cve_2017_7504`           | CVE-2017-7504    |
| 22   | CVE-2017-5941    | `docker pull vulfocus/nodejs-cve_2017_594`           | CVE-2017-5941    |
| 23   | CVE-2017-5638    | `docker pull vulfocus/struts2-cve_2017_5638`         | CVE-2017-5638    |
| 24   | CVE-2017-3066    | `docker pull vulfocus/coldfision-cve_2017_3066`      | CVE-2017-3066    |
| 25   | CNVD-2017-02833  | `docker pull vulfocus/fastjson-cnvd_2017_02833`      | CNVD-2017-02833  |
| 26   | CVE-2016-10033   | `docker pull vulfocus/wordpress-cve_2016_10033`      | CVE-2016-10033   |
| 27   | CVE-2016-9565    | `docker pull vulfocus/nagios-cve_2016_9565`          | CVE-2016-9565    |
| 28   | CVE-2016-4437    | `docker pull vulfocus/shiro-cve_2016_4437`           | CVE-2016-4437    |
| 29   | CVE-2014-3120    | `docker pull vulfocus/elasticsearch-cve_2014_3120`   | CVE-2014-3120    |


## 镜像新增日志

2020-04-27

- vulfocus/weblogic-cve_2020_2551
- vulfocus/joomla-cve_2020_10238_10239_11890
- vulfocus/weblogic-cve_2020_2555
- vulfocus/weblogic-cve_2020_2883
