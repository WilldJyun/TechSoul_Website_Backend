from flask import Flask,request,send_from_directory
from flask_restful import Resource, Api
from database_operate_module import TenX_DatabaseOperate
from Global_Vars import *
import json
import time
import os

class Pic_bed_class(Resource):
    def get(self):
        file_name = request.args.get('name')

        return send_from_directory(os.path.join(os.path.dirname(__file__), 'pic'), file_name)