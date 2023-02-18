# Telegram-group-index
A script to index all the media within a group.

TG 群媒体索引脚本

## 由来

众所周知 TG 对于中文搜索的支持非常不准确，经常会出现搜索不到文件的情况，所以便有了这个脚本。该脚本通过遍历所有历史消息，将文件名以及标题存入数据库来实现全局模糊搜索。

## 索引范围
- 文件名
- 文件标题（Caption）

TG 压缩过可预览的图片均不带文件名，如果有标题会被索引，无标题则不会；

通过移动端上传的压缩后可在线播放的视频均不带文件名，如果有标题会被索引，无标题则不会；

# 如何使用

## 安装依赖
`pip3 install uvloop pymysql`

`pip3 install -U https://github.com/pyrogram/pyrogram/archive/master.zip`

## 设置变量
`api_id`  `api_hash` : https://my.telegram.org/

`admin` : 使用者的账号 ID

`db_host` `db_user` `db_pwd` : 依次为 MySQL 数据库的主机地址，用户名和密码

`database`: 需要索引的群对应的数据库名，填写格式： {`一群ID`:`"一群数据库名"`, `二群ID`: `"二群数据库名"`} ， 示例可以参见 py 文件

## 运行

新建数据库并导入 `db.sql` 文件，

`python3 tgindex.py`

## 初始索引

使用者在群内发送 `/initdb` 会收到"开始创建索引"的回复，索引创建完成后会收到"索引完成"的回复。

群索引不会自动刷新，后续如果需要追加更新的索引，在群内发送 `/updatedb` 即可。

程序设置的索引速度为每秒20条，但 TG 可能会限流导致实际速度低于预期。

## 搜索资源

任意群成员都可以使用 `/search 关键词` 来进行搜索，请注意只支持一个关键词。搜索到的结果会以消息的形式返回，数量上限为按消息 ID 升序排序的前8条。

## 运行速度
在 2v CPU 2G RAM 的虚拟机上，搜索行数为34560的数据库，大约需要0.02-0.03秒时间。
