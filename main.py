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
                return {'result': 'failed','message': 'The schedule is not exist.'},404
        else:
            return {'result': 'failed','message': 'Week parameter is required'}, 400
            
api.add_resource(Schedule, '/api/schedule')

# 处理Notice返回逻辑

class Notice(Resource):

    # 声明类型
    type : str # Page/其他功能
    page : str # Type为Page时，返回页码

    def get(self):

        type = request.args.get('type')
        page = request.args.get('page')

        notifications : list # 查询到的符合条件的通知们
        if not type:
            return {'result': 'failed','message': '需要type参数 type parameter is required'}, 400
        
        if not page:
            return {'result': 'failed','message': '需要page参数 page parameter is required'}, 400
        
        if type == "all":

            if page == "0":
                counts = DatabaseOperate.Select_Database("Notifications",f"ORDER BY id DESC LIMIT {Global_ShowPages};",Count = True)
            
                result = {
                    "counts": counts, # 总条数
                    "itemsPerPage": Global_ShowPages, # 每页显示的条数
                }
                return result
            else:
                try:
                    ThePage = (int(page) -1 )* 5
                except: 
                    return {'result': 'failed','message': 'Page parameter is invalid,provide a integer'}, 400
                
                return DatabaseOperate.Select_Database("Notifications",f"ORDER BY id DESC LIMIT {Global_ShowPages} OFFSET {ThePage};")

        if type == "valid":

            current_time = time.strftime("%Y%m%d") # 取现行时间

            if page == "0":
                counts = DatabaseOperate.Select_Database("Notifications",f"WHERE Valid >= {current_time} ",Count = True) # 查询符合条件的通知总数
            
                result = {
                    "counts": counts, # 总条数
                    "itemsPerPage": Global_ShowPages, # 每页显示的条数
                }
                return result
            
            else:
                try:
                    ThePage = (int(page) - 1) * 5
                except: 
                    return {'result': 'failed','message': 'Page parameter is invalid,provide a integer'}, 400
                

                return DatabaseOperate.Select_Database("Notifications",f"WHERE Valid >= {current_time} ORDER BY id DESC LIMIT {Global_ShowPages} OFFSET {ThePage};")
            
        return {'result': 'failed','message': 'Invalid Requests.'}, 400

    NoticeData : str # 要添加的数据
    ModifyData : str # 要修改的数据
    DeleteData : str # 要删除的数据

    token : str # 输入token以获得写通知权限。 
    data : str # 接收到的原始请求json

    def post(self):

        data : dict = request.get_json()
        if "params" in data:
            params = data['params'] # 接收到的参数，里面params涵盖了所有信息

            if "Operate" not in params:
                return {'result': 'failed','message': '"Operate" Parameter is required'}, 400
            
            if params["Operate"] == "add":
            
                if "NoticeData" in params:

                    return self.AddContent(params["NoticeData"])
                # 添加通知，处理NoticeData
                
                return {'result': 'failed','message': '"NoticeData" Parameter is required'}, 400
                

            if params["Operate"] == "modify":

                if "ModifyData" in params:

                    return self.ModifyContent(params["ModifyData"])
                # 修改通知，处理ModifyData

                return {'result': 'failed','message': '"ModifyData" Parameter is required'}, 400
                
            if params["Operate"] == "delete":
                if "DeleteData" in params:

                    return self.DeleteContent(params["DeleteData"])
                # 删除通知，处理DeleteData

                return {'result': 'failed','message': '"DeleteData" Parameter is required'}, 400
                
            return {'result': 'failed','message': '"Operate" Parameter is required'}, 400

        return {'result': 'failed','message': '"Params" Parameter is required'}, 400
    
    def AddContent(self,NoticeData):
        """
        添加通知
        params:
            NoticeData: dict 通知内容

        returns:
            dict: 返回的结果

        """

        
        try:

            token = NoticeData["Token"]

            title = NoticeData["Title"]
            type = NoticeData["Type"]
            sender = NoticeData["Sender"]
            content = NoticeData["Content"]
            valid = NoticeData["Valid"]
        except Exception as e:
            return {'error': '缺失必要的项 make sure you have Token,Title,Type,Sender,Content,Valid'}, 400

        if token == Global_Temp_Token:
            
            current_time = time.strftime("%Y%m%d")
            try:
                DatabaseOperate.hang_on = True # 延缓下一次关闭数据库，防止被关闭无法操作
                Latest = DatabaseOperate.Select_Database("Notifications","ORDER BY id DESC LIMIT 1;") # 最新的通知
                
                if Latest["UID"]: # 如果最新的UID存在的话
                    UID = Latest["UID"] # 获取最新的UID
                    if UID[0:8] == current_time: # 如果日期（前八位）相同，就让后面编号自增1
                        local = int(UID[8:]) # 临时变量，储存末尾的自增序列号
                        local += 1 # 序列号自增1
                        UID = f"{current_time}{local}" # 自增完加到末尾
                    else: # 如果日期（前八位）不同，就让UID为当天的第一个通知
                        UID = f"{current_time}1"
                else: # 如果没有任何通知，就让UID为当天的第一个通知
                    UID = f"{current_time}1"
            except:
                UID = f"{current_time}1"

            DatabaseOperate.Insert_Database("Notifications",{
                "Title":title,
                "Type":type,
                "Sender":sender,
                "Content":content,
                "Valid":valid,
                "UID":UID,
                })



            back = {  # 成功处理，返回结果
                'Date':current_time,
                'Title':title,
                'Sender':sender,
            } 

            return back

        return "密码错误，添加失败"

    def ModifyContent(self,ModifyData):
        try:
            token = ModifyData["Token"]
            title = ModifyData["Title"]
            type = ModifyData["Type"]
            sender = ModifyData["Sender"]
            content = ModifyData["Content"]
            valid = ModifyData["Valid"]
            UID = ModifyData["UID"]

            send = {
                "Title":title,
                "Type":type,
                "Sender":sender,
                "Content":content,
                "Valid":valid,
            }

            if token == Global_Temp_Token:
                DatabaseOperate.Update_Database("Notifications",f"UID = {UID}", send)
        except:
            return {'result': 'failed','message': '缺失必要的项 make sure you have UID,Token,Title,Type,Sender,Content,Valid'}, 400
        
        
    def DeleteContent(self,DeleteData):
        try:
            token = DeleteData["Token"]
            UID = DeleteData["UID"]

            if token == Global_Temp_Token:
                DatabaseOperate.Delete_Database("Notifications",f"UID = {UID}")
        except:
            return {'error': '缺失必要的项 make sure you have UID,Token'}, 400
        
        return "删除成功"
        
    
        
api.add_resource(Notice, '/api/notice') # 监听路由


class DatabaseOperate():

    db : pymysql.connect
    hang_on : bool = False # 延缓下一次关闭数据库，防止被关闭无法操作

    @staticmethod
    def initialise() -> None:
        DatabaseOperate.db= pymysql.connect(db="TenX",host="localhost",user=Global_Username,password=Global_Password,port=Global_ConnectionPort)

    @staticmethod
    # 查询操作
    def Select_Database(TableName : str,Attribute : str = "",Count :bool = False) -> list: 
        """
        连接到数据库，并进行查询操作
        params:
            TableName: Str 表名
            Attribute: Str 属性
            （Attribute是from {TableName} 后的sql命令，、
            自己根据需要加sql语句。）

            Count: bool 是否返回计数
            如果Count为True，返回一个int值，表示查询到的结果数量。
        returns:
            list：消息

        """
        DatabaseOperate.initialise()
        # 使用cursor()方法获取操作游标
        cur = DatabaseOperate.db.cursor()

        if Count == True:
            sql = f"SELECT COUNT(*) FROM {TableName} {Attribute}"
            try:
                cur.execute(sql) 	#执行sql语句

                results = cur.fetchall()	#获取查询的所有记录
                #遍历结果
                return results[0][0] # 直接返回条数
            except Exception as e:
                raise e
        else:
            sql = f"SELECT * FROM {TableName} {Attribute}"
        
            notices = [] # 最终的消息列表
            try:
                cur.execute(sql) 	#执行sql语句

                results = cur.fetchall()	#获取查询的所有记录
                #遍历结果
                for row in results :
                    notices.append({
                        "UID": row[6],
                        "Title": row[1],
                        "Type": row[2],
                        "Sender": row[3],
                        "Content": row[4],
                        "valid": str(row[5]),
                    })
            except Exception as e:
                raise e
            finally:
                if DatabaseOperate.hang_on == True:
                    DatabaseOperate.hang_on = False
                else:
                    DatabaseOperate.db.close()	#关闭连接
            return notices
    
    @staticmethod
    def Insert_Database(TableName:str,Content:dict) -> bool:
        """
        连接到数据库，并进行插入操作
        插入格式为
        {
            "Title": " ",
            "Type": " ",
            "Sender": " ",
            "Content": " ",
            "Valid": " ",
        }
        UID会在此程序中自己生成。
        returns:
            bool：插入成功返回True，插入失败抛出异常

        """
        DatabaseOperate.initialise()
        try:

            # 使用cursor()方法获取操作游标
            cur = DatabaseOperate.db.cursor()

            # 2.插入操作
            # 编写sql 查询语句 对应 表名Notifications
            # 使用参数化查询，防止注入
            sql = f"INSERT INTO {TableName} (title, type, sender, content, valid, UID) VALUES (%s, %s, %s, %s, %s, %s)"

            values = (Content["Title"], Content["Type"], Content["Sender"], Content["Content"], Content["Valid"], Content["UID"])

            cur.execute(sql, values)  # 执行sql语句
            DatabaseOperate.db.commit()
            
            turnback = {
                "result": "success",
                "message": f"插入数据成功，UID{Content['UID']},Title{Content['Title']}"
            } # 返回结果

            return turnback
        except Exception as e:
            DatabaseOperate.db.rollback()
            raise e
        finally:
            if DatabaseOperate.hang_on == True:
                DatabaseOperate.hang_on = False
            else:
                DatabaseOperate.db.close()



    @staticmethod
    def Update_Database(TableName:str,Condition:str,UpdateDict:dict) -> bool:
        """
        连接到数据库，并进行更新操作
        params:
            TableName: Str 表名
            Condition: Str 更新条件
            UpdateDict: Dict 更新内容

        examples：
            Update_Database("Notifications","id = 1",{"Title":"Test","Type":"test","Sender":"test","Content":"test","Valid":"test"})

        returns:
            bool：更新成功返回True，更新失败抛出异常

        """
        DatabaseOperate.initialise()
        try:
            cur = DatabaseOperate.db.cursor()  # 获取游标

            # 构造更新内容
            update_items = [f"{key} = %s" for key in UpdateDict.keys()]
            update_str = ', '.join(update_items)

            # 构建 SQL 语句
            sql = f"UPDATE {TableName} SET {update_str} WHERE {Condition}"

            # 准备参数列表
            params = list(UpdateDict.values())

            # 执行 SQL 语句
            cur.execute(sql, params)
            DatabaseOperate.db.commit()  # 提交

        except Exception as e:
            # 回滚
            DatabaseOperate.db.rollback()
            raise e
        finally:
            if DatabaseOperate.hang_on == True:
                DatabaseOperate.hang_on = False
            else:
                DatabaseOperate.db.close()

        turnback = {
                "result": "success",
                "message": f"更新数据成功，依照条件：{Condition}"
            } # 返回结果
        return turnback
    @staticmethod
    def Delete_Database(TableName:str,Condition:str):
        """
        连接到数据库，并进行删除操作

        params:
            TableName: Str 表名
            Condition: Str 删除条件

        returns:
            list：所有消息

        """
        DatabaseOperate.initialise()
        try:

            # 使用cursor()方法获取操作游标
            cur = DatabaseOperate.db.cursor()

            # 3.删除操作
            # 编写sql 查询语句 对应 表名Notifications
            sql = f"DELETE FROM {TableName} WHERE {Condition}" 

            cur.execute(sql) 	#执行sql语句
            DatabaseOperate.db.commit()

        except Exception as e:

            DatabaseOperate.db.rollback() # 回滚
            raise e
        finally:
            if DatabaseOperate.hang_on == True:
                DatabaseOperate.hang_on = False
            else:
                DatabaseOperate.db.close()

        turnback = {
                "result": "success",
                "message": f"删除数据成功，依照条件：{Condition}"
            } # 返回结果
        return turnback
        
class Test(Resource):

    def get(self):
        a = DatabaseOperate()
        return a.Select_Database("Notifications","")

api.add_resource(Test, '/api/Test') # 监听路由

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
