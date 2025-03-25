from flask import request
from flask_restful import Resource
from Global_Vars import *
import random


content = """她 62 岁了，女性，没怎么上过学。
身高 150 厘米，体重 55 公斤。她从不抽烟喝酒。
家族里没有人得阿尔茨海默病，也没有心血管疾病和糖尿病。
她有过一次头部受伤，是几年前不小心摔倒撞到了头。
他没有抑郁症，但是有高血压。我每天会去楼下溜达溜达，身体活动量一般般，饮食就是家常便饭，睡眠质量不太好，容易醒。
我的收缩压 150 毫米汞柱，舒张压 90 毫米汞柱，总胆固醇 5.5，低密度脂蛋白胆固醇 3.0，高密度脂蛋白胆固醇 1.0，甘油三酯 1.5。
他有时候会忘记带钥匙，但是生活任务都能完成，也没有行为问题和人格改变，空间方向也没问题，就是有时候会有点糊涂。
简易精神状态检查表评分 22 分，日常生活活动能力表评分 90 分，
功能独立性评测我觉得自己算 4 分，需要一点帮助。"""

class Alzheimer_class(Resource):

    def get(self):
        API_providers = [
            {"url":"https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
             "api_key":"sk-9b72afeb2acb444384c368b88c412a4f",
             "model":"deepseek-v3"},
            {"url":"https://api.siliconflow.cn/v1/chat/completions",
             "api_key":"sk-ewrcuywrmemcssqkoajdkumoboiozmckjlcmrxehdvrdytyh",
             "model":"deepseek-ai/DeepSeek-V3"},
            ]
        choice = random.choice(API_providers)
        print(choice)
        return choice,200

    def post(self):

        data : dict = request.get_json()
        if not data:
            return {'result':'failed','message':'No data'},400
        
        if 'operate' not in data:
            return {'result':'failed','message':'operate not in data'},400
        
        if 'token' not in data:
            return {'result':'failed','message':'token not in data'},400
        
        if 'operate_data' not in data:
            return {'result':'failed','message':'operate_data not in data'},400
        
        # 以上为验证 operate, token, data 的操作
        operate_data = data['operate_data']

        if 'operate' == 'risk': # api: 计算得出风险值
            required_keys = [ # 检查是否包含所有必要的键！！重要，在此修改
                "Age",
                "Gender",
                "Ethnicity",
                "EducationLevel",
                "BMI",
                "Smoking",
                "AlcoholConsumption",
                "PhysicalActivity",
                "DietQuality",
                "SleepQuality",
                "FamilyHistoryAlzheimers",
                "CardiovascularDisease",
                "Diabetes",
                "Depression",
                "HeadInjury",
                "Hypertension",
                "SystolicBP",
                "DiastolicBP",
                "CholesterolTotal",
                "CholesterolLDL",
                "CholesterolHDL",
                "CholesterolTriglycerides"
            ]

            for key in required_keys:
                if key not in operate_data:
                    return {'result':'failed','message':f'{key} not in operate_data'},400
            
            # 下面是输入模型的逻辑
    
