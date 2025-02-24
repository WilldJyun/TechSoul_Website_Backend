# TenX 移动网站 开发文档
## TODO
- 前端
    - /app 页面
        - 课表页面UI连贯优化（翻页效果）
        - 课表页面尽量在屏幕内显示完整，避免向下滑动才能完整阅读的情况
        - 通知页面，换页按钮移到页面顶部，方便换页（或者固定在页面下方，避免拖动才能换页的情况）
        - 交流板块
            - 腾创班班委信箱
            - 团队匿名讨论
    - 主站页面
        - 博客、介绍、备案号
- 后端
    - 建立数据库，提供以下内容的读写支持
        - 账户系统
        - 通知、作业
        - 课表
        - 一些重要文件（迷你云盘）

## API
我们的后端是另外一个独立项目，前端、App等通过API进行访问。

所有API通过 

> tengchuang.top/api

访问。


# 1、获取课表的API
> GET tengchuang.top/api/schedule?week=1 

改变其中的 week 值 获得不同周的课表。
### 解释说明：返回通知的格式

通知组成：
> uid : 通知条目的唯一编号  
> title : 标题  
> type : 类型  
> sender : 发送者  
> valid : 有效日期，在此日期前有效

标识ID（UID）的命名为 发送时间YYYYMMDD + 自增序列号

自增序列号的长度不限，日期固定是前八位

当消息被添加时：取历史最新一条消息，若当前消息添加时间与历史最新一条消息时间相同，就让自增序列号自增1而日期不变；若时间不同或没有最新一条消息，就让UID变为当前的日期，自增序列号为1：YYYYMMDD1

（在数据库存储时，每一个数据会获得自己的排序id（自增），与UID不同，用于快速取出前x项。最新保存的项会获得最大的排序id。第一个存入的，排序id为1，第二个存入的为2，第1000个存入的为1000，以此类推）

# 2、 获取通知列表API

参数：
> type : 类型（valid或为all）   
> page : 页数（取0为页码数。取数字为页数）
改变其中的 page 值 获得对应页数的通知，**每页最多5条**。
## type = valid
### 1  输入页码 page = xx
> GET tengchuang.top/api/notice?type=valid&page=1
页数为1，后端会根据排序ID，取最新（排序ID最大）的5条通知；页数为2，取6~10条（如果存在），以此类推
返回的json格式：  
### **（注意大小写）**
~~~json
[
  {
    "uid": 202411201,
    "title": "通知标题1",
    "type": "通知类型1",
    "sender": "发送者1",
    "content": "通知内容1",
    "valid": "20241123"
  },
  {
    "uid": 202411202,
    "title": "通知标题2",
    "type": "通知类型2",
    "sender": "发送者2",
    "content": "通知内容1",
    "valid": "20241124"
  }
]
~~~

注释：
> 通知标题不超过30字,  
> 通知类型不超过10字,  
> 发送者不超过10字,  
> 通知内容不超过5000字。

### 2  当 page 值 为 0 时，返回所有通知的**条数**与每页显示的**条数**
> GET tengchuang.top/api/notice?type=valid&page=0
（如12项通知，5条/页）
~~~json
{
    "counts": 12,
    "slice": 5
}
~~~

## type = all
### 1 输入页码 page = xx，返回对应通知，无论是否过期
> GET tengchuang.top/api/notice?type=all&page=1
### 2 当 page 值 为 0 时，返回所有通知的**条数**与每页显示的**条数**，无论是否过期。
> GET tengchuang.top/api/notice?type=all&page=0

# 3、通知 操作
## 3.1 添加通知
> POST tengchuang.top/api/notice

POST发送的json格式：  
（注意大小写）
~~~json
{
    "operate": "add",
    "params": {
        "token": "口令，如果正确才能添加通知",
        "title": "通知标题",
        "type": "通知类型（作业等）",
        "sender": "发送者",
        "content": "通知内容",
        "valid": "在此日期前有效（含当日）"
    }
}
~~~
在 NoticeData 中 输入 Token、Title、Type、Sender、Content、Valid，令Operate = "add"，并用 params 包起来，通过 JSON 格式发送。

开发环境中token为123456，正式环境待定。

发送成功后，服务器会返回一个 JSON，格式如下：

返回的json格式：
~~~json
{
  "result": "success/failed",
  "message": "成功/失败原因"
}
~~~

## 3.2 更改已有通知
> POST tengchuang.top/api/notice

在前端的更改页面，应该先获取通知的UID、发送者、标题什么的，   
先在页面中填入原有的通知消息，   
因为更改是相当于完全更改，假设你只改标题，其他不变，   
那就用户会看到原来的消息，仅需更改标题，其他不变，发送整个新表单过来，后端会自动根据UID，覆盖发送者、标题、内容等。   

（注意大小写）

POST发送的json格式：
~~~json
{
    "operate": "update",
    "params": {
        "token": "口令，如果正确才能添加通知",
        "title": "通知标题",
        "type": "通知类型（作业等）",
        "sender": "发送者",
        "content": "通知内容",
        "valid": "在此日期前有效（含当日）"
    }
}

~~~
在 ModifyData 中 输入 要更改的UID，以及对应的Token、Title、Type、Sender、Content、Valid，令Operate = "modify"，并用 params 包起来，通过 JSON 格式发送。

开发环境中token为123456，正式环境待定。

发送成功后，服务器会返回一个 JSON，格式如下：

返回的json格式：
~~~json
{
  "result": "success/failed",
  "message": "成功/失败原因"
}
~~~

## 3.3 删除通知
> POST tengchuang.top/api/notice

（注意大小写）

POST发送的json格式：
~~~json
{
    "operate": "add",
    "params": {
        "token": "口令，如果正确才能删除通知",
        "uid": "通知的UID",
    }
}
~~~
开发环境中token为123456，正式环境待定。

发送成功后，服务器会返回一个 JSON，格式如下：
返回的json格式：
~~~json
{
  "result": "success/failed",
  "message": "成功/失败原因"
}
~~~

# 4、GPA查询功能（部分涉隐私）
> POST tengchuang.top/api/gpa

（注意大小写）

POST发送的json格式：
~~~json
{
    "operate": "GPA",
    "params": {
        "studentID": "学号",
        "password": "密码",
    }
}
~~~

返回格式例：

失败（会有具体原因）：
~~~json
{'status':'error','message':'Wrong Password or StudentID'}
~~~

成功：
~~~json
{
  'name':'姓名',
  'studentID':'学号',
  'GPA':'综合绩点情况',
  'rank':'排名情况',
  'time':'查询时间，内容是 %Y-%m-%d %H:%M:%S'
}
~~~
