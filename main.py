from flask import Flask,request,send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
import os
import json
import time
import pymysql #导入 pymysql
from Global_Vars import *

app = Flask (__name__)
api = Api(app)

# 启用CORS
CORS(app, resources={r"/*": {"origins": "*", "headers": ["Origin", "X-Requested-With", "Content-Type", "token", "Accept"]}})
# 处理课表返回逻辑

class Schedule(Resource):

    week : str # 周数

    def get(self):
        

        week = request.args.get('week')

        if week:
            try:
                # 课表文件路径
                file_path = f'schedule/{week}.json'
                # 获取当前脚本的目录
                current_dir = os.path.dirname(__file__)

                return send_from_directory(current_dir, file_path)
            except Exception as e:
                return {'error': 'The schedule is not exist.'},404
        else:
            return {'error': 'Week parameter is required'}, 400
            
api.add_resource(Schedule, '/api/schedule')

# 处理Notice返回逻辑

class Notice(Resource):

    # 声明类型
    type : str # Page/其他功能
    page : str # Type为Page时，返回页码

    def get(self):
        type = request.args.get('type')
        page = request.args.get('page')
        if type:
            if type == 'page':
                if page:
                    if page == "0":
                        return {"提示":"所有页的通知"}
                    else:
                        return {"提示":f"第{page}页的通知"}
                

    noticeData : str # 要添加的数据
    token : str # 输入token以获得写通知权限。
    data : str # 接收到的原始请求json

    def post(self):

        data : str = request.get_json()
        

        if 'params' in data:
            params = data['params'] # 接收到的参数，里面params涵盖了所有信息
            noticeData = params.get('noticeData') # 从params提取出noticeData一项

            if noticeData:
                try:
                    noticeData = json.loads(noticeData)  # 将 noticeData 从字符串解析为 JSON 对象
                except json.JSONDecodeError as e:
                    return {'error': 'Invalid JSON format for noticeData'}, 400

                token = noticeData.get('token')
                title = noticeData.get('title')
                sender = noticeData.get('sender')
                content = noticeData.get('content')

                if token and token == '123456':
                    app.logger.info(f"添加成功，标题：{title}, 发送者：{sender}, 内容：{content}")
                    current_time = time.strftime("%Y-%m-%d")

                    back = {  # 返回的结果
                        'title':title,
                        'sender':sender,
                        'content':content,
                        'date':current_time
                    } 

                    return back
                else:
                    app.logger.error("密码错误，添加失败")
                    return "密码错误，添加失败"
            else:
                return {'错误': '需要noticeData参数'}, 400
        else:
            return {'错误': '需要params参数，里面封装noticeData参数'}, 400


    def ModifyContent(self):
        pass
    def DeleteContent(self):
        pass
    
    def SaveLogToDB(self):
        pass
        
api.add_resource(Notice, '/api/notice') # 监听路由


class DatabaseOperate():

    db : pymysql.connect

    def __init__(self) -> None:
        DatabaseOperate.db= pymysql.connect(db="TenX",host="localhost",user=Global_Username,password=Global_Password,port=Global_ConnectionPort)
    def Select_Database(self,Type:str) -> list: 
        """
        连接到数据库，并进行查询操作

        returns:
            list：所有消息

        """
        # 使用cursor()方法获取操作游标
        cur = DatabaseOperate.db.cursor()

        #1.查询操作
        # 编写sql 查询语句 对应 表名Notifications
        sql = "select * from Notifications"
        
        notices = [] # 最终的消息列表
        try:
            cur.execute(sql) 	#执行sql语句

            results = cur.fetchall()	#获取查询的所有记录
            #遍历结果
            for row in results :
                notices.append({
                    "UID": row[6],
                    "title": row[1],
                    "type": row[2],
                    "sender": row[3],
                    "content": row[4],
                    "valid": str(row[5]),
                })
        except Exception as e:
            raise e
        finally:
            DatabaseOperate.db.close()	#关闭连接
        return notices

    def Insert_Database(self,TableName:str,Content:dict) -> bool:
        """
        连接到数据库，并进行插入操作
        插入格式为

        returns:
            bool：插入成功返回True，插入失败抛出异常

        """
        try:

            # 使用cursor()方法获取操作游标
            cur = DatabaseOperate.db.cursor()

            # 2.插入操作
            # 编写sql 查询语句 对应 表名Notifications
            sql = "INSERT INTO Notifications (title,type,sender,content,valid,UID) VALUES ('%s','%s','%s','%s','%s','%s')" % (Content["title"],Content["type"],Content["sender"],Content["content"],Content["valid"],Content["UID"])

            cur.execute(sql) 	#执行sql语句
            DatabaseOperate.db.commit()
            DatabaseOperate.db.close() # 关闭连接
            return True
        except Exception as e:
            DatabaseOperate.db.rollback()
            DatabaseOperate.db.close()
            raise e



    def Update_Database(self,TableName:str,Condition:str,UpdateDice:dict) -> bool:
        """
        连接到数据库，并进行更新操作
        params:
            TableName: Str 表名
            Condition: Str 更新条件
            UpdateDice: Dict 更新内容

        examples：
            Update_Database("Notifications","id = 1",{"title":"test","type":"test","sender":"test","content":"test","valid":"test"})

        returns:
            bool：更新成功返回True，更新失败抛出异常

        """
        try:

            cur = DatabaseOperate.db.cursor() # 来个游标

            update_str = ', '.join([f'{key} = "{value}"' for key, value in UpdateDice.items()]) # 构造更新内容

            sql = f"UPDATE {TableName} SET {update_str} WHERE {Condition}" # 构建sql语句

            cur.execute(sql) 	#执行sql语句
            DatabaseOperate.db.commit() # 提交
            DatabaseOperate.db.close() # 关闭连接
            return True
        except Exception as e:
            # 回滚
            DatabaseOperate.db.rollback()

            # 关闭连接
            DatabaseOperate.db.close()

            raise e

    def Delete_Database(self,TableName:str,Condition:str):
        """
        连接到数据库，并进行删除操作

        params:
            TableName: Str 表名
            Condition: Str 删除条件

        returns:
            list：所有消息

        """
        try:

            # 使用cursor()方法获取操作游标
            cur = DatabaseOperate.db.cursor()

            # 3.删除操作
            # 编写sql 查询语句 对应 表名Notifications
            sql = f"DELETE FROM {TableName} WHERE {Condition}" 

            cur.execute(sql) 	#执行sql语句
            DatabaseOperate.db.commit()
            DatabaseOperate.db.close() # 关闭连接
            return True
        except Exception as e:

            DatabaseOperate.db.rollback() # 回滚

            DatabaseOperate.db.close() # 关闭连接

            raise e
        
class Test(Resource):

    def get(self):
        a = DatabaseOperate()
        return a.Insert_Database("Notifications",{"title":"titletest","type":"typetest","sender":"sendertest","content":"contenttest","valid":"validtest","UID":"uidtest"})

api.add_resource(Test, '/api/Test') # 监听路由

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
    a = Database_Operate()