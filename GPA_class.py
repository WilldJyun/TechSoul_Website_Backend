from flask import Flask,request
from flask_restful import Resource, Api
from database_operate_module import GPA_DatabaseOperate
from Global_Vars import *
import json
from datetime import datetime
class GPA_class(Resource):
    def post(self):

            data : dict = request.get_json()
            if not data:
                return {'result':'failed','message':'No data'},400
            
            if 'operate' not in data:
                return {'result':'failed','message':'operate not in data'},400
            
            if data['operate'] == 'GPA':
                if 'params' not in data:
                    return {'result':'failed','message':'params not in data'},400
                params = data['params']
                print(params)

                if 'studentID' not in params: # 注意大小写，下同
                    return {'result':'failed','message':'studentID not in data'},400
                
                if 'password' not in params:
                    return {'result':'failed','message':'password not in data'},400
                
                GPA_DatabaseOperate.initialise()
                result = GPA_DatabaseOperate.CheckPassword(params['studentID'],params['password'])
                if result == False:
                    return {'result':'failed','message':'Wrong password or studentID'},400 # 查询有误，返回这个
                    
                try:
                # 查询成功
                    now = datetime.now()
                    turnback = {
                        'name':result['name'],
                        'studentID':params['studentID'],
                        'GPA':result['GPA'],
                        'rank':f"{result['rank']} / 31 人（班内排名）", # 后续需要在这里修改查询结果
                        'time':now.strftime('%Y-%m-%d %H:%M:%S')
                    } # 返回结果
                    return {'result':'success','message':turnback},200
                
                except Exception as e:
                    print(e)
                    return {'result':'failed','message':'Invalid input. 输入格式可能不正确'},400
            
