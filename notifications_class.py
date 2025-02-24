from flask import Flask,request
from flask_restful import Resource, Api
from database_operate_module import TenX_DatabaseOperate
from Global_Vars import *
import json
import time

class NotificationsClass(Resource):

    # 声明类型
    type : str # Page/其他功能
    page : str # type为Page时，返回页码

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
                counts = TenX_DatabaseOperate.Select_Database(Global_Table_Notifications,f"ORDER BY id DESC LIMIT {Global_ShowPages};",Count = True)
            
                result = {
                    "counts": counts, # 总条数
                    "slice": Global_ShowPages, # 每页显示的条数
                }
                return result
            else:
                try:
                    ThePage = (int(page) -1 )* 5
                except: 
                    return {'result': 'failed','message': 'Page parameter is invalid,provide a integer'}, 400
                
                return TenX_DatabaseOperate.Select_Database(Global_Table_Notifications,f"ORDER BY id DESC LIMIT {Global_ShowPages} OFFSET {ThePage};")

        if type == "valid":

            current_time = time.strftime("%Y%m%d") # 取现行时间

            if page == "0":
                counts = TenX_DatabaseOperate.Select_Database(Global_Table_Notifications,f"WHERE valid >= {current_time} ",Count = True) # 查询符合条件的通知总数
            
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
                

                return TenX_DatabaseOperate.Select_Database(Global_Table_Notifications,f"WHERE valid >= {current_time} ORDER BY id DESC LIMIT {Global_ShowPages} OFFSET {ThePage};")
            
        return {'result': 'failed','message': 'Invalid Requests.'}, 400

    notice_data : str # 要添加的数据
    update_data : str # 要修改的数据
    delete_data : str # 要删除的数据

    token : str # 输入token以获得写通知权限。 
    data : str # 接收到的原始请求json

    def post(self):

        data : dict = request.get_json()

        if "params" in data:
            params = data['params'] # 接收到的参数，里面params涵盖了所有信息

            if "operate" not in params:
                return {'result': 'failed','message': '"operate" Parameter is required'}, 400
            
            if params["operate"] == "add":
            
                if "notice_data" in params:

                    return self.AddContent(params["notice_data"])
                # 添加通知，处理NoticeData
                
                return {'result': 'failed','message': '"notice_data" Parameter is required'}, 400
                

            if params["operate"] == "update":

                if "update_data" in params:

                    return self.UpdateContent(params["update_data"])
                # 修改通知，处理update_data

                return {'result': 'failed','message': '"update_data" Parameter is required'}, 400
                
            if params["operate"] == "delete":
                if "delete_data" in params:

                    return self.DeleteContent(params["delete_data"])
                # 删除通知，处理DeleteData

                return {'result': 'failed','message': '"delete_data" Parameter is required'}, 400
                
            return {'result': 'failed','message': '"operate" Parameter is required'}, 400

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

            token = NoticeData["token"]

            title = NoticeData["title"]
            type = NoticeData["type"]
            sender = NoticeData["sender"]
            content = NoticeData["content"]
            valid = NoticeData["valid"]
        except Exception as e:
            return {'error': '缺失必要的项 make sure you have token,title,type,sender,content,valid'}, 400

        if token == Global_Temp_Token:
            
            current_time = time.strftime("%Y%m%d")
            TenX_DatabaseOperate.hang_on = True # 延缓下一次关闭数据库，防止被关闭无法操作
            Latest = TenX_DatabaseOperate.Select_Database(Global_Table_Notifications,"ORDER BY id DESC LIMIT 1;") # 最新的通知
            print(Latest)
            if "uid" in Latest[0]: # 如果最新的uid存在的话
                uid = Latest[0]["uid"] # 获取最新的uid
                if uid[0:8] == current_time: # 如果日期（前八位）相同，就让后面编号自增1
                    local = int(uid[8:]) # 临时变量，储存末尾的自增序列号
                    local += 1 # 序列号自增1
                    uid = f"{current_time}{local}" # 自增完加到末尾
                else: # 如果日期（前八位）不同，就让uid为当天的第一个通知
                    uid = f"{current_time}1"
            else: # 如果没有任何通知，就让uid为当天的第一个通知
                uid = f"{current_time}1"

            TenX_DatabaseOperate.Insert_Database(Global_Table_Notifications,{
                "title":title,
                "type":type,
                "sender":sender,
                "content":content,
                "valid":valid,
                "uid":uid,
                })



            back = {  # 成功处理，返回结果
                "result":"success",
                "message":f"添加成功，uid为{uid}",
            } 

            return back

        return "密码错误，添加失败"

    def UpdateContent(self,update_data):
        try:
            token = update_data["token"]
            title = update_data["title"]
            type = update_data["type"]
            sender = update_data["sender"]
            content = update_data["content"]
            valid = update_data["valid"]
            uid = update_data["uid"]

            send = {
                "title":title,
                "type":type,
                "sender":sender,
                "content":content,
                "valid":valid,
            }

            if token == Global_Temp_Token:
                result = TenX_DatabaseOperate.Update_Database(Global_Table_Notifications,f"uid = {uid}", send)
                return result
        except:
            return {'result': 'failed','message': '缺失必要的项 make sure you have uid,token,title,type,sender,content,valid'}, 400
        
        
    def DeleteContent(self,DeleteData):
        try:
            token = DeleteData["token"]
            uid = DeleteData["uid"]

            if token == Global_Temp_Token:
                result = TenX_DatabaseOperate.Delete_Database(Global_Table_Notifications,f"uid = {uid}")
                return result
        except:
            return {'result': 'failed','message': '缺失必要的项 make sure you have uid'}, 400

        
        return {'result': 'failed','message': f'未知错误，发生于notifications_class.py的DeleteContent函数'}