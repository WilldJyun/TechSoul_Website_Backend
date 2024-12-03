import pymysql
from global_vars import *

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
            （Attribute是FROM {TableName} 后的sql命令，、
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
                        "uid": row[6],
                        "title": row[1],
                        "type": row[2],
                        "sender": row[3],
                        "content": row[4],
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
    def Insert_Database(TableName:str,content:dict) -> bool:
        """
        连接到数据库，并进行插入操作
        插入格式按readme.md来。

        uid会在此程序中自己生成。
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
            sql = f"INSERT INTO {TableName} (title, type, sender, content, valid, uid) VALUES (%s, %s, %s, %s, %s, %s)"

            values = (content["title"], content["type"], content["sender"], content["content"], content["valid"], content["uid"])

            cur.execute(sql, values)  # 执行sql语句
            DatabaseOperate.db.commit()
            
            turnback = {
                "result": "success",
                "message": f"插入数据到{TableName}成功，uid{content['uid']}"
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
    def Update_Database(TableName:str,Condition:str,UpdateDict:dict):
        """
        连接到数据库，并进行更新操作
        params:
            TableName: Str 表名
            Condition: Str 更新条件
            UpdateDict: Dict 更新内容

        examples：
            Update_Database("Notifications","id = 1",{"title":"Test","type":"test","sender":"test","content":"test","valid":"test"})

        returns:
            dict (按照readme规范)

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