from flask import Flask,request
from flask_restful import Resource, Api
from database_operate_module import GPA_DatabaseOperate
from Global_Vars import *
import json
from datetime import datetime
import requests
from openai import OpenAI
import re
import concurrent.futures

client = OpenAI(
    api_key="sk-ewrcuywrmemcssqkoajdkumoboiozmckjlcmrxehdvrdytyh", # 从https://cloud.siliconflow.cn/account/ak获取
    base_url="https://api.siliconflow.cn/v1"
)
prompt1 = """
你是一个填表师，具有基础的医学与健康常识。
这是用户的情况自述，请你把用户的情况合理填入以下json表，你的最终输出应为如下格式的json表格。未提供的字段留空。请注意，你只能填写数字
~~~json
{
    "Age": "年龄",
    "Gender": "性别（0为男，1为女）",
    "EducationLevel": "教育程度（0为无，1为中小学，2为本科，3为硕博）",
    "Height": "身高",
    "Weight": "体重（公斤）",
    "BMI": "BMI"
}
~~~
不要输出任何多余内容。
如果用户在胡言乱语或说无关内容，请你输出"Error"。
"""

prompt2 = """
你是一个判断师，具有基础的医学与健康常识。
这是用户的情况自述，请你把用户的情况合理填入以下json表，对于每一项，你只有0、1两种填法，0代表否，1代表是。你的最终输出应为如下格式的json表格。若用户未提及则填0。
~~~json
{
    "Smoking": "吸烟情况",
    "AlcoholConsumption": "饮酒情况",
    "FamilyHistoryAlzheimers": "阿尔茨海默病家族史",
    "CardiovascularDisease": "心血管疾病",
    "Diabetes": "糖尿病",
    "Depression": "抑郁症",
    "HeadInjury": "头部受伤史",
    "Hypertension": "高血压",
}
~~~
不要输出任何多余内容。
如果用户在胡言乱语或说无关内容，请你输出"Error"。
"""

prompt3 = """
你是一个打分师，具有基础的医学与健康常识。
这是用户的情况自述，请你把用户的情况合理填入以下json表，对于每一项，你根据用户的描述进行打分，范围为数字0~10。你的最终输出应为如下格式的json表格。未提供的字段留空。
~~~json
{
    "PhysicalActivity": "身体活动量（每周运动1小时为1分，超过10小时为10分）",
    "DietQuality": "饮食质量",
    "SleepQuality": "睡眠质量",
}
~~~
不要输出任何多余内容。
如果用户在胡言乱语或说无关内容，请你输出"Error"。
"""

prompt4 = """
你是一个医师，具有基础的医学与健康常识。
这是用户的情况自述，请你把用户的情况合理填入以下json表，对于每一项，你根据用户的描述进行填写。你的最终输出应为如下格式的json表格。未提供的字段留空。
~~~json
{
    "SystolicBP": "收缩压 MmHg（毫米汞柱）",
    "DiastolicBP": "舒张压 MmHg（毫米汞柱）",
    "CholesterolTotal": "总胆固醇 TC",
    "CholesterolLDL": "低密度脂蛋白胆固醇 mmol/L",
    "CholesterolHDL": "高密度脂蛋白胆固醇 mmol/L",
    "CholesterolTriglycerides": "甘油三酯 mmol/L",
    "MMSE（Mini-Mental State Examination）": "简易精神状态检查表评分 0~30分",
    "ADL（Activities of Daily Living）": "日常生活活动能力表评分 1~126分",
    "FunctionalAssessment": "功能独立性评测 1~7",
}
~~~
数据库：
MMSE评分参考：
痴呆评分参考:
27: 正常（良好、优秀）
21: 轻度
15: 中度
5: 重度
FunctionalAssessment 评分参考：

独立：活动中不需他人帮助7分：完全独立-- 构成活动的所有作业均能规范、完全地完成，不需修改和辅助设备或用品，并在合理的时间内完成。6分：有条件的独立-- 具有下列一项或几项：活动中需要辅助设备；活动需要比正常长的时间；或有安全方面的考虑。



依赖：为了进行活动，患者需要另一个人予以监护或身体的接触性帮助，或者不进行活动有条件的依赖--患者付出50%或更多的努力，其所需的辅助水平如下：5分：监护和准备-- 患者所需的帮助只限于备用、提示或劝告，帮助者和患者之间没有身体的接触或帮助者仅需要帮助准备必需用品；或帮助戴上矫形器。4分：少量身体接触的帮助-- 患者所需的帮助只限于轻轻接触，自己能付出75%或以上的努力。3分：中度身体接触的帮助-- 患者需要中度的帮助，自己能付出50%~75%的努力。完全依赖：患者需要一半以上的帮助或完全依赖他人，否则活动就不能进行。2分：大量身体接触的帮助-- 患者付出的努力小于50%，但大于25%。1分：完全依赖-- 患者付出的努力小于25%。
不要输出任何多余内容。
如果用户在胡言乱语或说无关内容，请你输出"Error"。
"""

prompt5 = """
你是一个判断师，具有基础的医学与健康常识。
这是用户的情况自述，请你把用户的情况合理填入以下json表，对于每一项，你只有0、1两种填法，0代表否，1代表是。你的最终输出应为如下格式的json表格。如果你确信用户确实未提及相关内容，应填0。
~~~json
{
    "MemoryComplaints": "记忆方面的主诉",
    "BehavioralProblems": "行为问题",
    "Confusion": "是否有困惑、糊涂症状",
    "Disorientation": "是否有空间方向定向障碍情况",
    "PersonalityChanges": "是否有人格改变",
    "DifficultyCompletingTasks": "是否难以完成生活任务",
    "Forgetfulness": "是否健忘",
}
~~~
不要输出任何多余内容。
如果用户在胡言乱语或说无关内容，请你输出"Error"。
"""

def get_json_from_ai(prompt : str, content : str):
    response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": content}
            ],
            # response_format={"type": "json_object"}
        )
    print("成功")
    return response.choices[0].message.content

# content = """
# 我今年 63 岁了，性别女，只上过小学。
# 身高 155 厘米，体重 60 公斤。年轻时候在工厂做工，现在退休在家带孙子。
# 每天下午去公园散步 1 小时，周末会跳广场舞。
# 饮食比较清淡，爱吃豆腐和青菜，但口味偏咸。睡眠还行，就是半夜总要起夜两三次。
# 老伴抽烟三十多年了，我自己不抽烟但经常吸二手烟。逢年过节会喝一小杯黄酒。
# 父亲前些年得了老年痴呆，母亲有高血压。我自己去年体检发现胆固醇偏高（总胆固醇 5.8，低密度 3.2），
# 血压 130/85。最近老是忘记关煤气，上周去菜市场差点迷路。女儿说我最近脾气变得急躁，常把衣服穿反。
# 上个月简易精神状态检查得了 24 分，日常生活能力评分 85 分，现在自己做饭洗澡没问题，但系鞋带需要女儿帮忙
# """

content = """她 62 岁了，女性，没怎么上过学。"""
content = """她 62 岁了，女性，没怎么上过学。
身高 150 厘米，体重 55 公斤。她从不抽烟喝酒。
家族里没有人得阿尔茨海默病，也没有心血管疾病和糖尿病。
她有过一次头部受伤，是几年前不小心摔倒撞到了头。
他没有抑郁症，但是有高血压。我每天会去楼下溜达溜达，身体活动量一般般，饮食就是家常便饭，睡眠质量不太好，容易醒。
我的收缩压 150 毫米汞柱，舒张压 90 毫米汞柱，总胆固醇 5.5，低密度脂蛋白胆固醇 3.0，高密度脂蛋白胆固醇 1.0，甘油三酯 1.5。
他有时候会忘记带钥匙，但是生活任务都能完成，也没有行为问题和人格改变，空间方向也没问题，就是有时候会有点糊涂。
简易精神状态检查表评分 22 分，日常生活活动能力表评分 90 分，
功能独立性评测我觉得自己算 4 分，需要一点帮助。"""
prompts = [prompt5, prompt4, prompt3, prompt2, prompt1]
json_texts = []

# 使用 ThreadPoolExecutor 实现并发请求
with concurrent.futures.ThreadPoolExecutor() as executor:
    future_to_prompt = {executor.submit(get_json_from_ai, prompt, content): prompt for prompt in prompts}
    
    for future in concurrent.futures.as_completed(future_to_prompt):
        prompt = future_to_prompt[future]
        try:
            response = future.result()
            if response != "Error":
                match_ans = re.search(r"\{.*\}", response, re.DOTALL)
                if match_ans:
                    json_text = match_ans.group(0).strip()  # 去除前后多余空格和换行符
                    json_texts.append(json_text)
                else:
                    print(f"无法找到 prompt 返回的 JSON 字符串: {response}")
            else:
                print(f"对于 prompt 返回了 Error")
        except Exception as exc:
            print(f"Prompt 处理时发生异常: {exc}")

# 手动合并 JSON 文本
if json_texts:
    # 去除每个 JSON 文本的 `{` 和 `}`，并去除多余空格和换行符，然后合并
    combined_json = "{\n" + ",\n".join([json_text.strip("{}").strip() for json_text in json_texts]) + "\n}"
    print(combined_json)
else:
    print("没有有效的 JSON 响应")