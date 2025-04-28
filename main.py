from flask import Flask,request,send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
import os
import time
from notifications_class import NotificationsClass
from Global_Vars import *
from database_operate_module import *
from GPA_class import GPA_class
from Alzheimer_class import Alzheimer_class
from Pic_bed import Pic_bed_class

app = Flask (__name__)
api = Api(app)

allowed_origins = [
    "https://ai.tengchuang.top",
    "https://tengchuang.top"
]

def cors_allow(app):
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        if origin in allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Headers'] = "Origin, X-Requested-With, Content-Type, token, Accept"
        return response
    return app

app = cors_allow(app)
CORS(app)
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
api.add_resource(NotificationsClass, '/api/notice') # 监听路由

# 处理GPA返回逻辑（隐私）
api.add_resource(GPA_class, '/api/gpa') # 监听路由

# 处理 阿尔兹海默症相关 返回逻辑
api.add_resource(Alzheimer_class, '/api/ad')

class Test(Resource):

    def get(self):
        a = TenX_DatabaseOperate()
        return a.Select_Database("Notifications","")

api.add_resource(Test, '/api/Test') # 监听路由

# 自制图床
api.add_resource(Pic_bed_class, '/api/pic')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
