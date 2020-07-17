# struts2-045（CVE-2017-5638）by [xiajibaxie](https://github.com/xiajibaxie)

## 漏洞描述

安恒信息安全研究院WEBIN实验室高级安全研究员 nike.zheng 发现著名 J2EE 框架—— Struts2 存在远程代码执行的严重漏洞; 目前 Struts2 官方已经确认漏洞（漏洞编号 S2-045 ， CVE 编号： CVE-2017-5638 ），并定级为高风险。

## 影响版本

Struts 2.3.5 – Struts 2.3.31
Struts 2.5 – Struts 2.5.10

## 利用流程

访问地址： `10.10.11.20:54169`

名称：vulfocus/struts-045

使用Struts2全版本漏洞测试工具获取 flag 成功

![1](./1.png)



通关！

## 参考

https://blog.csdn.net/rossrocket/article/details/67674290

