risk = {}
index = 0
condition = False
operate_data = {
    "BMI":24.4,
    'SystolicBP':138,
    'DiastolicBP':25,
    'AlcoholConsumption':10,
    "PhysicalActivity":9,
    "DietQuality":8,
    "SleepQuality":7,
    "FamilyHistoryAlzheimers":1,
    "CardiovascularDisease":1,
    "Diabetes":1,
    "Depression":1,
    "HeadInjury":1,
    "Hypertension":1,
    "SystolicBP":1,
}

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
    if float(operate_data['SystolicBP']) > 130 or float(operate_data['DiastolicBP']) > 80 : 
        index += 1
        risk.update({str(index):f"您的血压过高（收缩压{operate_data['SystolicBP']} / 舒张压{operate_data['DiastolicBP']}）"})
        condition = 1
else:
    if int(operate_data["Hypertension"]) == 1:
        index += 1
        risk.update({str(index):f"您患有高血压，请寻找医师获得专业指导"})
        condition = 1

if float(operate_data['AlcoholConsumption']) > 10 : 
    index += 1
    risk.update({str(index):"您饮酒过量，少喝酒有益健康"})

if float(operate_data['DietQuality']) < 6 : 
    index += 1
    risk.update({str(index):"您的饮食质量较差，请寻找医师获得专业指导"})
    condition = 1

if float(operate_data['SleepQuality']) < 6 : 
    index += 1
    risk.update({str(index):"您的饮食质量较差，请寻找医师获得专业指导"})
    condition = 1

if int(operate_data["CardiovascularDisease"]) == 1 :
    index += 1
    risk.update({str(index):"您有心血管疾病，请寻找医师获得专业指导"})
    condition = 1

if int(operate_data["Diabetes"]) == 1 :
    index += 1
    risk.update({str(index):"您患有糖尿病，请寻找医师获得专业指导"})
    condition = 1

if int(operate_data["Depression"]) == 1 :
    index += 1
    risk.update({str(index):"您患有抑郁症，请寻找医师获得专业指导"})
    condition = 1

if int(operate_data["HeadInjury"]) == 1 :
    index += 1
    risk.update({str(index):"您有过头部受伤历史，若严重不适，请寻找医师获得专业指导"})


# 下面是输入预测模型的逻辑
try:
    possibility = "cnm"
    messsage = {
        "possibility":possibility,
        "condition": condition),
        "risks": risk,
    }
    print ({'result':'success','message':messsage},200)
except Exception as e:
    print ({'result':'failed','message':str(e)},400)

