import json

# 假设你已经得到了以下 JSON 字符串
json_str1 = '{"Age": "63", "Gender": "1", "EducationLevel": "1", "Height": "155", "Weight": "60", "BMI": ""}'
json_str2 = '{"Smoking": "0", "AlcoholConsumption": "1", "FamilyHistoryAlzheimers": "1", "CardiovascularDisease": "0", "Diabetes": "0", "Depression": "0", "HeadInjury": "0", "Hypertension": "1"}'
json_str3 = '{"PhysicalActivity": "2", "DietQuality": "5", "SleepQuality": "3"}'
json_str4 = '{"SystolicBP": "130", "DiastolicBP": "85", "CholesterolTotal": "5.8", "CholesterolLDL": "3.2", "CholesterolHDL": "", "CholesterolTriglycerides": "", "MMSE": "24", "ADL": "85", "FunctionalAssessment": "4"}'
json_str5 = '{"MemoryComplaints": "1", "BehavioralProblems": "0", "Confusion": "1", "Disorientation": "1", "PersonalityChanges": "1", "DifficultyCompletingTasks": "0", "Forgetfulness": "1"}'

# 解析 JSON 字符串
json_obj1 = json.loads(json_str1)
json_obj2 = json.loads(json_str2)
json_obj3 = json.loads(json_str3)
json_obj4 = json.loads(json_str4)
json_obj5 = json.loads(json_str5)

# 合并所有字典
merged_json_obj = {**json_obj1, **json_obj2, **json_obj3, **json_obj4, **json_obj5}

# 打印合并后的 JSON 对象
print(json.dumps(merged_json_obj, ensure_ascii=False, indent=4))
