import os
import json

#定义个人数据文件路径
DATA_FILE = os.path.join("data", "user_profile.json")

def load_profile():
    """加载个人用户数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"summary" : "新用户" , "details": {}}

def save_profile(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE,'w', encoding='utf-8') as f:
        json.dump(data, f , ensure_ascii=False, indent=4)