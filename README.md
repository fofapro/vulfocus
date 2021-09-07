<h1 align="center"> Welcome to Vulfocus 🚀 </h1>

Vulfocus 是一个漏洞集成平台，将漏洞环境 docker 镜像，放入即可使用，开箱即用。

<p>
  <img src="https://img.shields.io/github/stars/fofapro/vulfocus.svg?style=flat-square" />
  <img src="https://img.shields.io/github/release/fofapro/vulfocus.svg?style=flat-square" />
  <img src="https://img.shields.io/github/release/fofapro/vulfocus.svg?color=blue&label=update&style=flat-square" />
  <img src="https://img.shields.io/github/license/fofapro/vulfocus?style=flat-square" />
  <!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
<img src="https://img.shields.io/badge/all_contributors-24-orange.svg?style=flat-square" />
<!-- ALL-CONTRIBUTORS-BADGE:END -->
</p>

Vulfocus 官网：[https://fofapro.github.io/vulfocus/](https://fofapro.github.io/vulfocus/)

在线 Vulfocus：

[http://vulfocus.fofa.so/](http://vulfocus.fofa.so/)

[http://vulfocus.io/](http://vulfocus.io/)

[http://vulfocus.club/](http://vulfocus.club/)

## 背景

漏洞靶场是目前每个安全人员以及想学习信息安全的人必备的东西，但目前商业化产品居多，还有一些类似 dvwa、 sqli-labs 这类的开源项目，但是漏洞环境比较固定，使用完一次后就失去其作用。搭建的成本过高，每次启动的流程会比较繁琐，甚至很多场景是不满足的，之前关于漏洞环境镜像使用多的是 vulhub，但是作为企业、高校等以及相关的培训，单纯的漏洞环境不一定能满足使用的需求，所以我们基于当下的一些靶场项目做出了小小的改进来符合我们的一些需求，比如增加 flag 的形式，来满足一些考核与验证的需求，可以对我们内部人员能力进行考核，于是 Vulfocus 就诞生了。

## 认识 Vulfocus

因为 Vulfocus 一个漏洞集成平台，所以可以无限向里添加漏洞环境没有限制，前提是你的内存足够大。因为漏洞环境是docker镜像的原因每次重新启动漏洞环境都会还原，不用出现你会对环境造成破坏下次无法启动的现象。

Vulfocus 的 docker 仓库 [https://hub.docker.com/u/vulfocus](https://hub.docker.com/u/vulfocus)

### Vulfocus的特性


1. 启动：一键漏洞环境启动，方便简单。
2. 自带 Flag 功能：每次启动 flag 都会自动更新，明确漏洞是否利用成功。
3. 带有计分功能也可适用于相关安全人员能力的考核。
4. 兼容 [Vulhub](https://vulhub.org/)、[Vulapps](http://vulapps.evalbug.com/) 中所有漏洞镜像。
5. 支持可视化编排漏洞环境

## 使用

![](./imgs/10.png)


1. 安装完成后，访问80端口

2. 用设置好的管理员账户登录

3. 首页为漏洞集成页面，刚开始是没有漏洞镜像的需要从 [https://hub.docker.com/](https://hub.docker.com/) 网站拉取镜像，或自己以tar包的形式上传。

   漏洞镜像的拉取和上传（**需管理员权限**）：

   (1)、在进行管理中，添加功能

   ![](./imgs/image.gif)

   (2)、分别填入漏洞名称、镜像、rank、描述

   - 镜像又分为文件和文本
  - 文本：是从 [https://hub.docker.com/u/vulfocus](https://hub.docker.com/u/vulfocus) 官网拉取镜像。内容为如： `vulfocus/webmin-cve_2019_15107` 。
     - 文件：本地漏洞镜像打成tar包的形式进行上传。

4. 下载完成后点击启动即可。

5. 镜像启动后，会在环境里写入一个 flag （默认 flag 会写入 **/tmp/** 下），读取到 flag 后填入 flag 窗口，镜像会自动关闭，如需重新启动，需强刷一下，然后再次点击启动即可。

6. 可视化编排（管理员权限）

![](./imgs/8.gif)

7. 场景模式（普通用户权限）

![](./imgs/9.gif)

8. 计时模式

![](./imgs/11.gif)

## 合作伙伴

>  按注册顺序排序，欢迎用户在 [https://github.com/fofapro/vulfocus/issues/198](https://github.com/fofapro/vulfocus/issues/198) 登记（仅供社区参考）

<table>
<tr>
<td><a href="http://www.sinorail.com/" target="_blank">中铁信网络技术研究院</a></td>
<td><a href="http://www.snnu.edu.cn/" target="_blank"><img src="./cooperate/snnu.png"  width="190px" height="80px" alt="陕西师范大学"></a></td>
<td><a href="http://www.baimaohui.net/" target="_blank"><img src="./cooperate/baimaohui.png"  width="190px" height="80px" alt="白帽汇安全研究院"></a></td>
<td><a href="https://github.com/0verSp4ce" target="_blank"><img src="./cooperate/0verSp4ce.png" width="190px" height="80px" alt="凌驭空间（OverSpace）安全团队"></a></td>
</tr>
<tr>
<td><a href="https://red-team.cn/" target="_blank"><img src="./cooperate/red-team.png" width="190px" height="80px" alt="公鸡队之家·知识星球"></a></td>
<td><a href="https://www.sierting.com/" target="_blank"><img src="./cooperate/sierting.png" width="190px" height="80px" alt="克拉玛依市思而听网络科技有限公司"></a></td>
<td><a href="https://wx.zsxq.com/dweb2/index/group/88512188158852" target="_blank">赛博回忆录</a></td>
<td><a href="https://github.com/medicean/vulapps" target="_blank">VulApps</a></td>
</tr>
<tr>
<td><a href="https://www.huoxian.cn" target="_blank"><img src="./cooperate/huoxian.png"  width="190px" height="80px" alt="火线平台"></a></td>
<td><a href="https://dongtai.io/" target="_blank"><img src="./cooperate/dongtai.png"  width="190px" height="80px" alt="洞态"></a></td>
<td><a href="#" target="_blank">建成信息安全科技有限公司</a></td>
<td><a href="#" target="_blank">FACday安全团队</a></td>
</tr>
<tr>
<td><a href="http://www.tmsec.net/" target="_blank">天幕安全团队</a></td>
<td><a href="https://github.com/vulhub/vulhub" target="_blank"><img src="./cooperate/vulhub.svg"  width="190px" height="80px" alt="Vulhub"></a></td>
</tr>
</table>

## FAQ

**镜像启动后立即访问地址失败？**

1. 根据镜像的大小，启动时间会有不同的延迟，一般在几秒以内。

**提交完 flag 后会有卡住？**

1. 在提交完正确flag后，会进行镜像关闭的动作，所以会有几秒的延迟。

**拉取镜像时一直卡在哪里**

1. 由于网络延迟或镜像太大的原因时间会长一点。

2. 镜像名称填错，也会卡在哪里，建议强刷一下。

**Centos 无权限操作Docker**

[centos7 docker版本应用无法添加镜像](https://github.com/fofapro/vulfocus/issues/6)

## Contributors

Thanks goes to these wonderful people :

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->

<table>
  <tr>
    <td align="center"><a href="https://github.com/anonymity3712"><img src="https://avatars0.githubusercontent.com/u/40228178?v=4?s=100" width="100px;" alt=""/><br /><sub><b>anonymity3712</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/issues?q=author%3Aanonymity3712" title="Bug reports">🐛</a> <a href="#blog-anonymity3712" title="Blogposts">📝</a></td>
    <td align="center"><a href="https://github.com/TC130"><img src="https://avatars2.githubusercontent.com/u/8563648?v=4?s=100" width="100px;" alt=""/><br /><sub><b>TC130</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/issues?q=author%3ATC130" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/hackwuli"><img src="https://avatars1.githubusercontent.com/u/47844992?v=4?s=100" width="100px;" alt=""/><br /><sub><b>hackwuli</b></sub></a><br /><a href="#question-hackwuli" title="Answering Questions">💬</a></td>
    <td align="center"><a href="https://github.com/lxyevil"><img src="https://avatars3.githubusercontent.com/u/17840712?v=4?s=100" width="100px;" alt=""/><br /><sub><b>lxyevil</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/commits?author=lxyevil" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/littleheary"><img src="https://avatars3.githubusercontent.com/u/26987382?v=4?s=100" width="100px;" alt=""/><br /><sub><b>littleheary</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/pulls?q=is%3Apr+reviewed-by%3Alittleheary" title="Reviewed Pull Requests">👀</a></td>
    <td align="center"><a href="https://github.com/q2118cs"><img src="https://avatars0.githubusercontent.com/u/18305067?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Rai Sun</b></sub></a><br /><a href="#ideas-q2118cs" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/luobei-Dynamic"><img src="https://avatars2.githubusercontent.com/u/13211734?v=4?s=100" width="100px;" alt=""/><br /><sub><b>luobei-Dynamic</b></sub></a><br /><a href="#ideas-luobei-Dynamic" title="Ideas, Planning, & Feedback">🤔</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/wanglaiqi"><img src="https://avatars3.githubusercontent.com/u/9366714?v=4?s=100" width="100px;" alt=""/><br /><sub><b>wanglaiqi</b></sub></a><br /><a href="#ideas-wanglaiqi" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/zhuhongchang1227"><img src="https://avatars2.githubusercontent.com/u/59280688?v=4?s=100" width="100px;" alt=""/><br /><sub><b>zhuhongchang1227</b></sub></a><br /><a href="#ideas-zhuhongchang1227" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/daibing125"><img src="https://avatars1.githubusercontent.com/u/49011861?v=4?s=100" width="100px;" alt=""/><br /><sub><b>daibing</b></sub></a><br /><a href="#ideas-daibing125" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/zhangfeitao"><img src="https://avatars0.githubusercontent.com/u/10626929?v=4?s=100" width="100px;" alt=""/><br /><sub><b>zhangfeitao</b></sub></a><br /><a href="#ideas-zhangfeitao" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/TORRYGUO"><img src="https://avatars0.githubusercontent.com/u/43666746?v=4?s=100" width="100px;" alt=""/><br /><sub><b>TORRYGUO</b></sub></a><br /><a href="#ideas-TORRYGUO" title="Ideas, Planning, & Feedback">🤔</a></td>
    <td align="center"><a href="https://github.com/Becivells"><img src="https://avatars2.githubusercontent.com/u/12883127?v=4?s=100" width="100px;" alt=""/><br /><sub><b>李大壮</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/commits?author=Becivells" title="Documentation">📖</a></td>
    <td align="center"><a href="https://github.com/Vdeem"><img src="https://avatars1.githubusercontent.com/u/24988893?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Vdeem</b></sub></a><br /><a href="#blog-Vdeem" title="Blogposts">📝</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/xiajibaxie"><img src="https://avatars2.githubusercontent.com/u/45410321?v=4?s=100" width="100px;" alt=""/><br /><sub><b>xiajibaxie</b></sub></a><br /><a href="#blog-xiajibaxie" title="Blogposts">📝</a> <a href="https://github.com/fofapro/vulfocus/commits?author=xiajibaxie" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/Frivolous-scholar"><img src="https://avatars0.githubusercontent.com/u/48624840?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Frivolous-scholar</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/commits?author=Frivolous-scholar" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/D4ch1au"><img src="https://avatars3.githubusercontent.com/u/46175208?v=4?s=100" width="100px;" alt=""/><br /><sub><b>D4ch1au</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/commits?author=D4ch1au" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/M2ayill"><img src="https://avatars2.githubusercontent.com/u/22850233?v=4?s=100" width="100px;" alt=""/><br /><sub><b>M2ayill</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/commits?author=m2ayill" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/Whippet0"><img src="https://avatars0.githubusercontent.com/u/46486374?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Whippet</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/commits?author=Whippet0" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/Aa1141415869"><img src="https://avatars1.githubusercontent.com/u/46923769?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Aa1141415869</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/commits?author=Aa1141415869" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/fengyehack"><img src="https://avatars2.githubusercontent.com/u/58175380?v=4?s=100" width="100px;" alt=""/><br /><sub><b>fengyehack</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/commits?author=fengyehack" title="Code">💻</a></td>
  </tr>
  <tr>
    <td align="center"><a href="https://github.com/wuli888"><img src="https://avatars1.githubusercontent.com/u/47844992?v=4?s=100" width="100px;" alt=""/><br /><sub><b>wuli</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/commits?author=wuli888" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/Liiuliu"><img src="https://avatars.githubusercontent.com/u/48509067?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Liiuliu</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/commits?author=Liiuliu" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/atdpa4sw0rd"><img src="https://avatars.githubusercontent.com/u/24519788?v=4?s=100" width="100px;" alt=""/><br /><sub><b>atdpa4sw0rd</b></sub></a><br /><a href="https://github.com/fofapro/vulfocus/commits?author=atdpa4sw0rd" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## 讨论区

如有问题可以在 GitHub 提 issue, 也可在下方的讨论组里

GitHub issue: [https://github.com/fofapro/vulfocus/issues](https://github.com/fofapro/vulfocus/issues)

微信群: 通过扫描以下二维码加入并且备注 `申请 Vulfocus` 加入 Vulfocus 官方微信群。

<img src="./imgs/wechat.jpeg" widht="500px" height="500px"  />

## 致谢

- [Vue Element Admin](https://github.com/PanJiaChen/vue-element-admin)
- [Vulhub](https://vulhub.org/)
- [VulApps](https://github.com/Medicean/VulApps)

## 声明

该项目会收集了当下比较流行的漏洞环境，若有侵权，请联系我们！

