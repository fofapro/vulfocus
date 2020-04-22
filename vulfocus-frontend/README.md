# vulfocus WEB

vulfocus 前端项目，通过 Element-ui + VUE 构建。

环境：
- UI：Element UI
- 框架：vue
- node：v12.16.2
- npm：6.14.4

## 部署

安装依赖：
```shell script
npm install 
```

构建项目：
```
npm run build:prod
```

将 dist 目录部署至 nginx 中，默认 nginx 静态目录位于 `/var/www/html`。

## 开发

```shell script
npm run dev
```

