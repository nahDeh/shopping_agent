import streamlit as st
import requests

#后端地址
try:
    BACKEND_URL = st.secrets["BACKEND_URL"]
except:
    BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI 导购 (客户端)", layout="wide")
st.title("🛍️ 你的专属 AI 导购")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("用户画像记忆")
    if st.button("记录画像"):
        try:
            res = requests.get(f"{BACKEND_URL}/profile?user_id=test_user")
            st.json(res.json())
        except:
            st.error("无法连接到后端服务器")


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("想买点什么？"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("连接大脑思考中..."):
            try:
                payload = {"user_id": "test_user", "message": prompt}
                response = requests.post(f"{BACKEND_URL}/chat", json=payload)

                if response.status_code == 200:
                    data = response.json()

                    reply = data["reply"]
                    st.markdown(reply)

                    if data["items"]:
                        col = st.columns(4)
                        for i , item in enumerate(data["items"]):
                            with col[i]:
                                if item["images"]:
                                    st.image(item["image"], use_container_width=True)
                                st.caption(item["title"][:20])
                                st.markdown(f"**item['price']**")
                                if item["link"]:
                                    st.link_button("购买", item["link"])

                    if data["new_profile"]:
                        st.toast("用户画像更新")

                    st.session_state.messages.append({"role": "assistant", "content": reply})

                else:
                    st.error(f"服务器报错: {response.status_code}")
                    
            except Exception as e:
                st.error(f"网络连接失败: {e}")