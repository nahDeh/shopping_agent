import json
from langchain_core.prompts import ChatPromptTemplate
from typing import Optional, Dict
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class ProfileUpdateResult(BaseModel):
    #用于判断用户喜好是否需要更新
    has_update: bool = Field(description="判断用户是否透露了新的偏好，需要更新画像则为 True，否则为 False")
    #根据has_update的返回值来进行判断来进行更新
    new_profile: Optional[dict] = Field(description="如果不更新，为 null；如果更新，输出融合后的完整画像 JSON 数据")

#创建观察者AI, 负责分析用户画像, 更新画像
def observer_agent(llm, user_input, current_profile):
    parser = PydanticOutputParser(pydantic_object=ProfileUpdateResult)

    prompt = f"""
    你是一个敏锐的用户画像侧写师。
    【当前画像】：{current_profile}
    【用户新语】："{user_input}"
    
    判断用户是否透露了新的购物偏好（预算、品牌、风格等）。
    请严格按照下方的格式说明输出JSON。

    {format_instruction}
    """

    chain = prompt | llm | parser

    try:
        result = chain.invoke({
            "current_profile": json.dumps(current_profile, ensure_ascii=False),
            "user_input" : user_input,
            "format_instruction" : parser.get_format_instructions()
        })

        if result.has_update:
            print(f"用户画像更新:{result.new_profile}")
            return result.new_profile
        else:
            return None
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
