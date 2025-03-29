from flask import request
from flask_restful import Resource
from Global_Vars import *
# import random
from alzheimer_infer.infer_with_possibility import predict

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
        API_providers = {"url":"https://api.siliconflow.cn/v1/chat/completions",
             "api_key":"sk-ewrcuywrmemcssqkoajdkumoboiozmckjlcmrxehdvrdytyh",
             "model":"deepseek-ai/DeepSeek-V3"},
            
        return API_providers,200

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
            ]

            for key in required_keys:
                if key not in operate_data:
                    return {'result':'failed','message':f'{key} not in operate_data'},400
                

            condition = False # 是否建议立刻就医
            risk = {} # 风险项目
            index = 0 # 风险序号

            if float(operate_data['BMI']) > 23.9 : 
                index += 1
                risk.update({str(index):f"BMI偏高（{operate_data['BMI']}），您的体重过高，建议控制体重"})

            if float(operate_data['BMI']) < 18.5 : 
                index += 1
                risk.update({str(index):f"BMI偏低（{operate_data['BMI']}），您的体重过低，建议注意饮食"})

            if "SystolicBP" in operate_data and "DiastolicBP" in operate_data:
                if float(operate_data['SystolicBP']) > 130 or float(operate_data['DiastolicBP']) > 80 or : 
                    index += 1
                    risk.update({str(index):f"您的血压过高（收缩压{operate_data['SystolicBP']} / 舒张压{operate_data['DiastolicBP']}）"})
                    condition = True
            else:
                if int(operate_data["Hypertension"]) == 1:
                    index += 1
                    risk.update({str(index):f"您患有高血压，请寻找医师获得专业指导"})
                    condition = True
            
            if float(operate_data['AlcoholConsumption']) > 10 : 
                index += 1
                risk.update({str(index):"您饮酒过量，少喝酒有益健康"})

            if float(operate_data['DietQuality']) < 6 : 
                index += 1
                risk.update({str(index):"您的饮食质量较差，请寻找医师获得专业指导"})
                condition = True

            if float(operate_data['SleepQuality']) < 6 : 
                index += 1
                risk.update({str(index):"您的饮食质量较差，请寻找医师获得专业指导"})
                condition = True

            if int(operate_data["CardiovascularDisease"]) == 1 :
                index += 1
                risk.update({str(index):"您有心血管疾病，请寻找医师获得专业指导"})
                condition = True

            if int(operate_data["Diabetes"]) == 1 :
                index += 1
                risk.update({str(index):"您患有糖尿病，请寻找医师获得专业指导"})
                condition = True

            if int(operate_data["Depression"]) == 1 :
                index += 1
                risk.update({str(index):"您患有抑郁症，请寻找医师获得专业指导"})
                condition = True

            if int(operate_data["HeadInjury"]) == 1 :
                index += 1
                risk.update({str(index):"您有过头部受伤历史，若严重不适，请寻找医师获得专业指导"})
            

            # 下面是输入预测模型的逻辑
            try:
                possibility = predict(operate_data)
                messsage = {
                    "possibility":possibility,
                    "condition": condition,
                    "risks": risk,
                }
                return {'result':'success','message':messsage},200
            except Exception as e:
                return {'result':'failed','message':str(e)},400
