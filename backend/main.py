from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import os
from core.agent import observer_agent, generate_search_agentkey, generate_advice
from core.search import search_shopping
from core.memory import load_profile, save_profile

from langchain_openai import ChatOpenAI


SILICON_API_KEY = os.getenv("SILICON_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
BASE_URL = os.getenv("BASEURL")
MODEL_NAME = os.getenv("MODEL_NAME")
if not SILICON_API_KEY:
    print("⚠️ 警告: 未检测到 SILICON_API_KEY，AI 功能将无法使用！")



llm = ChatOpenAI(
    openai_api_base=BASE_URL,
    openai_api_key=SILICON_API_KEY,
    model_name=MODEL_NAME,
    temperature=0.6
)
    
app = FastAPI(title="AI 导购 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许任何来源访问 (生产环境可以改成前端的具体网址)
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法 (POST, GET 等)
    allow_headers=["*"],  # 允许所有 Header
)

#=== 定义通信的数据格式 (Pydantic Model) ===
# 前端发过来的聊天请求格式
class ChatRequest(BaseModel):
    user_id: str          # 用于区分不同用户
    message: str          # 用户说的话

class ChatResponse(BaseModel):
    reply: str            # AI 的回复
    items: List[Dict] = [] # 推荐的商品列表
    new_profile: Optional[Dict] = None # 是否更新了画像

#对话接口, 前端对话时发送请求
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    user_msg = request.message
    
    #读取用户画像
    profile = load_profile()
    #将对话丢给观察者进行画像分析与写入
    new_profile = observer_agent(llm, user_msg, profile)
    if new_profile:
        save_profile(new_profile)
        profile = new_profile

    #生成关键词, 然后去搜索拿到结果
    keyword = generate_search_agentkey(llm, user_msg, profile['details'])
    search_res = search_shopping(keyword, SERPER_API_KEY)

    #将搜索的结果里的商品数据提取出来
    items_data = []
    items_text = []
    if search_res and "shopping" in search_res:
        for item in search_res["shopping"][:4]:
            items_data.append({
                "title": item.get("title"),
                "price": item.get("price"),
                "image": item.get("imageUrl"),
                "link": item.get("link")
            })
            items_text += f"- {item.get('title')} | {item.get('price')}\n"

    advice = generate_advice(llm, user_msg, profile['summary'], profile['details'], items_text)

    return ChatResponse(
        reply=advice,
        items=items_data,
        new_profile=new_profile
    )


#接口2 保存画像
@app.get("/profile")
async def get_profile(user_id: str):
    return load_profile()


if __name__ == "__main__":
    # 启动服务器，端口 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)