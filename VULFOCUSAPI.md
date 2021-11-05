# 镜像信息获取

镜像信息获取接口，通过GET请求，认证通过后返回所有镜像信息（镜像名称，漏洞名称，漏洞描述）

## 请求URI

`/api/imgs/operation  `

## 请求方法

`GET`

## 请求参数

| 参数名   | 类型   | 说明                                                   | 举例                                |
| -------- | ------ | ------------------------------------------------------ | ----------------------------------- |
| username | string | 用户名                                                 | username=admin                      |
| licence  | string | 用户Licence，可登录vulfocus在用户界面 点击 Account查看 | licence=1da2sd1a565ad32a1d32a1sd32a |

## 响应参数

| 参数名                | 类型   | 说明     |
| --------------------- | ------ | -------- |
| data[].image_name     | string | 镜像名称 |
| data[].image_vul_name | string | 漏洞名称 |
| data[].image_desc     | string | 漏洞描述 |

### demo

```
# 成功
{"data": [{"image_name": "vulfocus/nuxeo-cve_2018_16341:latest", "image_vul_name": "nuxeo 命令执行 （CVE-2018-16341）", "image_desc": "Nuxeo Platform是一款跨平台开源的企业级内容管理系统(CMS)。\nnuxeo-jsf-ui组件处理facelet模板不当，当访问的facelet模板不存在时，相关的文件名会输出到错误页面上，而错误页面会当成模板被解析，文件名包含表达式也会被输出同时被解析执行，从而导致远程代码执行漏洞。\n用户名密码：Administrator:Administrator"}, {"image_name": "vulfocus/apache-cve_2021_41773:latest", "image_vul_name": "vulfocus/apache-cve_2021_41773", "image_desc": "Apache HTTP Server 2.4.49、2.4.50版本对路径规范化所做的更改中存在一个路径穿越漏洞，攻击者可利用该漏洞读取到Web目录外的其他文件，如系统配置文件、网站源码等，甚至在特定情况下，攻击者可构造恶意请求执行命令，控制服务器。"}, {"image_name": "vulfocus/wordpress-cve_2018_7422:latest", "image_vul_name": "wordpress 文件包含 （CVE-2018-7422）", "image_desc": "WordPress是WordPress软件基金会的一套使用PHP语言开发的博客平台，该平台支持在PHP和MySQL的服务器上架设个人博客网站。Site Editor plugin是使用在其中的一个所见即所得的前端编辑器。\n\nWordPress Site Editor插件1.1.1及之前版本中存在本地文件包含漏洞。远程攻击者可通过向editor/extensions/pagebuilder/includes/ajax_shortcode_pattern.php文件发送‘ajax_path’参数利用该漏洞检索任意文件。\n密码：admin     admin"}, {"image_name": "jboss/keycloak:latest", "image_vul_name": "jboss/keycloak", "image_desc": "jboss/keycloak"}], "status": 200, "msg": "OK"}
# 失败
{"data": null, "status": 500, "msg": "认证信息错误"}
```

# 镜像操作

镜像操作接口，通过此接口可以对镜像进行启动，停止，删除操作

## 请求URI

`/api/imgs/operation  `

## 请求方法

`POST`

## 请求参数

| 参数名      | 类型   | 说明                                                   | 举例                                              |
| ----------- | ------ | ------------------------------------------------------ | ------------------------------------------------- |
| username    | string | 用户名                                                 | username=admin                                    |
| licence     | string | 用户Licence，可登录vulfocus在用户界面 点击 Account查看 | licence=1da2sd1a565ad32a1d32a1sd32a               |
| image_name  | string | 镜像名称                                               | image_name=vulfocus/weblogic-cve_2018_2894:latest |
| requisition | string | 请求操作 start（启动）stop（停止）delete（删除）       | requistion=start                                  |

demo

```
POST /api/imgs/operation HTTP/1.1
Host: vulfocus.fofa.so
User-Agent: curl/7.64.1
Accept: */*
Content-Length: 126
Content-Type: application/x-www-form-urlencoded
Connection: close

username=admin&licence=eb9cd000c2904b6ab&image_name=vulfocus/struts2-cve_2016_3081:latest&requisition=start
```

## 响应参数

| 参数名 | 类型   | 说明             |
| ------ | ------ | ---------------- |
| host   | string | 返回容器请求地址 |
| port   | string | 返回端口信息     |

### demo

```
# 成功
{"data": {"host": "vulfocus.fofa.so:44963,61748,26663", "port": "{\"8080\": \"44963\", \"8787\": \"61748\", \"9443\": \"26663\"}"}, "status": 200, "msg": "启动成功"}
{"data": {"host": "vulfocus.fofa.so:44963,61748,26663", "port": "{\"8080\": \"44963\", \"8787\": \"61748\", \"9443\": \"26663\"}"}, "status": 200, "msg": "镜像已经启动"}
#失败
{"data": null, "status": 500, "msg": "认证信息错误"}
{"data": null, "status": 500, "msg": "启动失败"}
{"data": null, "status": 500, "msg": "镜像不存在"}
{"data": null, "status": 500, "msg": "停止镜像失败"}
{"data": null, "status": 500, "msg": "删除镜像失败"}

```



## 返回公共体

| 参数名 | 类型   | 说明     | 举例                                                         |
| ------ | ------ | -------- | ------------------------------------------------------------ |
| data   | json   | 返回信息 | {"host": "vulfocus.fofa.so:36130,61060", "port": "{\"3306\": \"36130\", \"80\": \"61060\"}"} |
| status | string | 返回状态 | "status": 200                                                |
| msg    | string | 返回原因 | "msg": "启动成功"                                            |

## status 状态

| 状态码 | 说明     | 返回信息                                                     |
| ------ | -------- | ------------------------------------------------------------ |
| 200    | 请求成功 | 返回镜像信息成功/启动成功/停止成功/删除成功                  |
| 500    | 请求失败 | 认证信息错误/镜像不存在/镜像名称不能为空/错误的请求/启动容器数量达到上线/启动失败/停止失败/ |

