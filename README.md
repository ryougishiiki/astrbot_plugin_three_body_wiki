# 灰机wiki查询插件


## 配置列表
 |配置名称|填写内容|
 |--------|-------|
 |站点名|灰机的子域名，例如查询三体wiki就填santi|
 |鉴权码|灰机wiki站外API访问需要鉴权码，否则会返回403|

 ## 指令列表
 ```yaml
 /wiki find <name>
 /wiki search <name>
 ```
在指定的灰机站点中搜索<name>
如果搜索到有关内容，返回格式如下:
```yaml
  查找到xxx个页面
  标题：概述
  链接：xxx
  ……
```
```yaml
/wiki-help
```
获取帮助列表
