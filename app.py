# -*- coding: utf-8 -*-
"""
Created on Tue May 12 21:17:27 2026

@author: Baize
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()



api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")

client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

st.set_page_config(
    page_title="SayFlow｜AI场景化表达助手",
    page_icon="💬",
    layout="wide"
)

st.title("💬 SayFlow｜AI 场景化表达助手")
st.caption("把想说的话，变成更合适、更自然、更能达成目标的表达。")

with st.sidebar:
    st.header("表达参数")

    scene = st.selectbox(
        "沟通场景",
        ["暧昧关系", "朋友关系", "职场沟通", "道歉修复", "拒绝别人", "表达不满", "面试回答"]
    )

    relation = st.selectbox(
        "关系距离",
        ["很亲近", "普通熟人", "上下级/同事", "刚认识", "关系紧张", "不确定"]
    )

    goal = st.selectbox(
        "表达目标",
        ["显得温柔", "保持边界", "推进关系", "避免冲突", "显得专业", "让对方重视", "缓和气氛"]
    )

    tone = st.selectbox(
        "语气风格",
        ["自然一点", "温柔一点", "高情商一点", "坚定一点", "可爱一点", "克制一点", "正式一点"]
    )

    intensity = st.slider("语气强度", 1, 5, 3)

user_input = st.text_area(
    "输入你原本想说的话",
    height=150,
    placeholder="例如：我今天不想去了，你们玩吧。"
)

def build_prompt(user_text, scene, relation, goal, tone, intensity):
    return f"""
你是一个中文 AI 场景化表达助手，目标是帮助用户把原话改写成更适合发送的表达。

请根据以下信息生成结果：

【用户原话】
{user_text}

【沟通场景】
{scene}

【关系距离】
{relation}

【表达目标】
{goal}

【语气风格】
{tone}

【语气强度】
{intensity}/5

请严格用 JSON 格式输出，不要输出多余解释。字段如下：

{{
  "recommended": "最推荐直接发送的版本",
  "versions": [
    {{
      "title": "自然版",
      "content": "改写内容",
      "reason": "为什么这样改",
      "risk": "可能的风险",
      "score": 4
    }},
    {{
      "title": "温柔版",
      "content": "改写内容",
      "reason": "为什么这样改",
      "risk": "可能的风险",
      "score": 4
    }},
    {{
      "title": "边界版",
      "content": "改写内容",
      "reason": "为什么这样改",
      "risk": "可能的风险",
      "score": 4
    }}
  ],
  "strategy": "整体表达策略分析",
  "avoid": ["不建议使用的表达1", "不建议使用的表达2", "不建议使用的表达3"]
}}

要求：
1. 输出必须自然，像真人会发出的中文消息。
2. 不要油腻，不要爹味，不要过度道歉。
3. 根据场景、关系、目标调整表达。
4. 如果是职场或面试场景，要更专业。
5. 如果是暧昧或朋友场景，要保留自然亲近感。
不要使用 Markdown 代码块，不要用 ``` 包裹 JSON。
"""

def generate_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "你是一个擅长中文表达改写的 AI 场景化表达助手。请严格按用户要求输出 JSON。"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return response.choices[0].message.content

if "history" not in st.session_state:
    st.session_state.history = []

if st.button("✨ 生成表达方案", use_container_width=True):
    if not user_input.strip():
        st.warning("先输入一句原话。")
    else:
        with st.spinner("正在生成更合适的表达方式..."):
            try:
                prompt = build_prompt(user_input, scene, relation, goal, tone, intensity)

                raw_output = generate_response(prompt).strip()

                if raw_output.startswith("```"):
                    raw_output = raw_output.replace("```json", "").replace("```", "").strip()

                result = json.loads(raw_output)

                st.session_state.history.insert(0, {
                    "input": user_input,
                    "scene": scene,
                    "goal": goal,
                    "result": result
                })

            except Exception as e:
                st.error("生成失败，可能是 API Key、模型名或 JSON 解析问题。")
                st.code(str(e))

if st.session_state.history:
    latest = st.session_state.history[0]
    result = latest["result"]

    st.subheader("✅ 推荐发送版")
    st.success(result["recommended"])

    st.subheader("📌 多版本表达")

    cols = st.columns(3)

    for idx, item in enumerate(result["versions"]):
        with cols[idx % 3]:
            st.markdown(f"### {item['title']}")
            st.write(item["content"])
            st.caption(f"推荐指数：{'⭐' * int(item['score'])}")
            with st.expander("查看分析"):
                st.write("**为什么这样说：**", item["reason"])
                st.write("**潜在风险：**", item["risk"])

    st.subheader("🧠 表达策略")
    st.info(result["strategy"])

    st.subheader("⚠️ 不建议这样说")
    for avoid_text in result["avoid"]:
        st.write(f"- {avoid_text}")

    st.divider()

    st.subheader("🕘 历史记录")
    for item in st.session_state.history[:5]:
        with st.expander(f"{item['scene']}｜{item['goal']}｜{item['input'][:20]}..."):
            st.write("原话：", item["input"])
            st.write("推荐：", item["result"]["recommended"])