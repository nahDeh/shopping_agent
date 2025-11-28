import json
import requests

def search_shopping(query, api_key):
    """调用apikey进行搜索"""
    if not api_key:
        return None
    
    url = "https://google.serper.dev/shopping"
    pyload = json.dumps({
        "q": query,
        "gl": "cn", 
        "hl": "zh-cn"
    })
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response =  requests.request("POST", url, headers=headers, data=pyload)
        print(response.json()) 
        return response.json()
    except Exception as e:
        print(f"搜索失败:{e}")
        return None