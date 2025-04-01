from flask import request
from flask_restful import Resource
from Global_Vars import *
# import random
from alzheimer_infer.infer_with_possibility import predict
from alzheimer_infer.risk_prompt import  get_not_predict_yet_prompt, get_low_risk_prompt, get_medium_high_risk_prompt, get_medium_low_risk_prompt, get_medium_risk_prompt

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

        if data['token'] != Global_Alzheimer_Temp_Token: # 验证token，接口鉴权
            return {'result':'failed','message':'token error'},400
        
# ==============================
        if data['operate'] == 'init': # api：获得尚未自查时的AI提示词
            return {'result':'success','message':get_not_predict_yet_prompt()},200
# ==============================

        
        if 'operate_data' not in data:
            return {'result':'failed','message':'operate_data not in data'},400
        
        # 以上为验证 operate, token, data 的操作
        operate_data = data['operate_data']


        


# ==============================
        if data['operate'] == 'risk': # api: 计算得出风险值，并得到相关风险、是否建议尽快就医、AI提示词
            required_keys = [ # 检查是否包含所有必要的键！！重要，在此修改
                "Age",
                "Gender",
                "EducationLevel",
                "Height",
                "Weight",
                "Smoking",
                "AlcoholConsumption", # 从0~20个酒精单位
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
                
            operate_data.update({"Ethnicity":2}) # 为亚洲人设计，默认为 2
            weight = int(operate_data["Weight"])
            height = int(operate_data["Height"])
            bmi = round(weight / (height/100)**2,1)
            operate_data.update({"BMI": bmi})

            condition = False # 是否建议立刻就医
            risk = {} # 风险项目

            if float(operate_data['BMI']) > 23.9 : 

                risk.update({"需要减肥":f"BMI偏高（{operate_data['BMI']}），您的体重过高，建议控制体重"})

            if float(operate_data['BMI']) < 18.5 : 

                risk.update({"体重过轻":f"BMI偏低（{operate_data['BMI']}），您的体重过低，建议注意饮食"})

            if "SystolicBP" in operate_data and "DiastolicBP" in operate_data:
                if float(operate_data['SystolicBP']) > 130 or float(operate_data['DiastolicBP']) > 80 : 
    
                    risk.update({"高血压":f"您的血压过高（收缩压{operate_data['SystolicBP']} / 舒张压{operate_data['DiastolicBP']}）"})
                    condition = True
            else:
                if int(operate_data["Hypertension"]) == 1:
    
                    risk.update({"高血压":f"您患有高血压"})
                    condition = True
            
            if float(operate_data['AlcoholConsumption']) > 10 : 

                risk.update({"饮酒过量":"您饮酒过量，少喝酒有益健康"})

            if float(operate_data['DietQuality']) < 6 : 

                risk.update({"饮食质量待提高":"您的饮食质量较差"})
                condition = True

            if float(operate_data['SleepQuality']) < 6 : 

                risk.update({"睡眠质量待提高":"您的睡眠质量较差"})
                condition = True

            if int(operate_data["CardiovascularDisease"]) == 1 :

                risk.update({"心血管疾病":"您有心血管疾病"})
                condition = True

            if int(operate_data["Diabetes"]) == 1 :

                risk.update({"糖尿病需重视":"您患有糖尿病"})
                condition = True

            if int(operate_data["Depression"]) == 1 :

                risk.update({"抑郁症需重视":"您患有抑郁症"})
                condition = True

            if int(operate_data["HeadInjury"]) == 1 :

                risk.update({"头部曾受伤":"您有过头部受伤历史，若严重不适，请寻找医师获得专业指导"})
            
            if "MMSE" in operate_data:
                if float(operate_data['MMSE']) <= 23 :
    
                    risk.update({"MMSE评分低":f"您的MMSE评分偏低，为{operate_data['MMSE']}"})
                    condition = True

            if "ADL" in operate_data:
                if float(operate_data['ADL']) <= 60 :
    
                    risk.update({"ADL评分低":f"您的ADL量表评分偏低，为{operate_data['ADL']}"})
                    condition = True
            if "Confusion" in operate_data:
                if int(operate_data['Confusion']) == 1:
    
                    risk.update({"感到困惑": "患阿尔兹海默症的老人常常感到迷茫与困惑，甚至在熟悉的地方也如此"})
                    condition = True

            if "Disorientation" in operate_data:
                if int(operate_data['Disorientation']) == 1:
    
                    risk.update({"迷失方向感": "患阿尔茨海默症的老人初期在方向感上“会出现偏差”，尤其“总会高估自己转弯的角度"})
                    condition = True

            if "PersonalityChanges" in operate_data:
                if int(operate_data['PersonalityChanges']) == 1:
    
                    risk.update({"性格行为变化": "责任心强、神经质程度低等性格人格可以延缓或防止阿尔兹海默症"})
                    condition = True

            if "DifficultyCompletingTasks" in operate_data:
                if int(operate_data['DifficultyCompletingTasks']) == 1:
    
                    risk.update({"对事务感到棘手": "您在完成日常任务时有困难"})
                    condition = True

            if "Forgetfulness" in operate_data:
                if int(operate_data['Forgetfulness']) == 1:
    
                    risk.update({"健忘": "建议关注自身的记忆力情况"})
                    condition = True


            
            # 下面是输入预测模型的逻辑
            try:
                possibility : int  # 风险值 
                possibility = predict(operate_data)

                final_possibility = f"{possibility}"
                age = operate_data['Age']
                gender = operate_data['Gender']
                if int(gender) == 0:
                    the_gender = "男"
                elif int(gender) == 1:
                    the_gender = "女"

                if possibility <= 20: # 低风险
                    prompt = get_low_risk_prompt(age, the_gender, final_possibility,risk)

                elif possibility > 20 and possibility <= 40: # 中低风险
                    prompt = get_medium_low_risk_prompt(age, the_gender, final_possibility,risk)

                elif possibility > 40 and possibility <= 60: # 中风险
                    prompt = get_medium_risk_prompt(age, the_gender, final_possibility,risk)

                elif possibility > 60: # 中高风险
                    prompt = get_medium_high_risk_prompt(age, the_gender, final_possibility,risk)
                    condition = True # 此时风险过高，建议用户寻求医师诊断。

                messsage = {
                    "possibility":final_possibility,
                    "condition": condition,
                    "risks": risk,
                    "prompt": prompt
                }
                return {'result':'success','message':messsage},200
            except Exception as e:
                return {'result':'failed','message':str(e)},400
# ===========================
        
        return {'result':'failed','message':'没有对应的operate选项'},400