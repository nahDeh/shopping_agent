import json
from langchain_core.prompts import ChatPromptTemplate

#创建观察者AI, 负责分析用户画像, 更新画像
def observer_agent(llm, user_input, current_profile):
    prompt = f"""
    你是一个敏锐的用户画像侧写师。
    【当前画像】：{json.dumps(current_profile, ensure_ascii=False)}
    【用户新语】："{user_input}"
    
    判断用户是否透露了新的购物偏好（预算、品牌、风格等）。
    - 无更新：输出 "NO_UPDATE"
    - 有更新：输出更新后的完整 JSON。保留旧数据，融合新数据。
    
    只输出 JSON。
    """

    try:
        response = llm.invoke(prompt).content
        if "NO_UPDATE" in response:
            return None
        clean_json = response.replace("```json", "").replace("```", "").strip()
        print(response)
        return json.loads(clean_json)
    except Exception as e:
        return None
    
#根据画像来将用户输入的语句进行精确分析,生成精准的搜索关键词
def generate_search_agentkey(llm, user_input, profile_details):
    prompt=f"""
    用户需求：{user_input}
    长期画像：{json.dumps(profile_details, ensure_ascii=False)}
    请生成一个用于购物平台的精准搜索关键词。例如 "罗技无线鼠标 200元内"
    """

    return llm.invoke(prompt).content.strip()

def generate_advice(llm, user_input, profile_summary, profile_details, items_context):
    prompt = f"""
    你是一个懂行的导购。
    【客户画像】：{profile_summary}
    【具体偏好】：{profile_details}
    【搜到的商品】：\n{items_context}
    【用户需求】：{user_input}
    
    请推荐 1-2 款，并解释理由。如果商品不符合画像，请直说。
    """

    return llm.invoke(prompt).content
