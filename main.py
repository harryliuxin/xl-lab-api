from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# 允许微信小程序域名（需替换为你的）
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://www.weixin.qq.com"],
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],  # 微信小程序会先发送 OPTIONS 预检请求
    allow_headers=["*"]
)

@app.post("/api/ai-tools")
async def ai_tools(request: Request):
    data = await request.json()
    user_prompt = data.get("prompt", "")
    
    # 调用你的AI逻辑（示例：直接返回输入内容）
    return {"response": f"AI处理结果: {user_prompt}"}