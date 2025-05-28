from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
from openai import OpenAI

app = FastAPI()

# 允许微信小程序域名（需替换为你的）
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://www.weixin.qq.com"],
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],  # 微信小程序会先发送 OPTIONS 预检请求
    allow_headers=["*"]
)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),  # 从.env加载
    base_url="https://api.deepseek.com/v1"  # 关键：修改API地址
)


def get_weather(city: str) -> dict:
    """调用OpenWeatherMap API获取天气数据"""
    API_KEY = os.getenv("OWM_API_KEY")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=zh_cn"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if response.status_code == 200:
            return {
                "temp": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "icon": data["weather"][0]["icon"]  # 用于后续显示天气图标
            }
        else:
            return {"error": f"API错误: {data.get('message', '未知错误')}"}
    except Exception as e:
        return {"error": f"网络异常: {str(e)}"}
    
def generate_anime_weather(city: str, weather_data: dict) -> str:
    """使用DeepSeek生成动漫风格天气"""
    prompt = f"""
    你是一个精通动漫的助手，请用以下规则描述天气：
    1. 结合知名动漫场景比喻（如《你的名字》《天气之子》）
    2. 语气活泼，加入颜文字(如~☆ヽ(≧▽≦)ﾉ)
    3. 根据天气推荐动漫角色穿搭
    4. 使用以下天气数据：
       - 城市: {city}
       - 温度: {weather_data['temp']}°C
       - 天气状况: {weather_data['description']}
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # DeepSeek专用模型
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=200
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ DeepSeek生成失败: {str(e)}"
    
async def weather(city: str):
    weather_data = get_weather(city)
    if "error" in weather_data:
        return(f"❌ 获取天气失败: {weather_data['error']}")
    else:
        basic_info = (
            f"🌆 {city}天气：\n"
            f"🌡️ 温度: {weather_data['temp']}°C\n"
            f"📝 描述: {weather_data['description']}\n"
            f"💧 湿度: {weather_data['humidity']}%"
        )
        anime_reply = generate_anime_weather(city, weather_data)
        return (f"{basic_info}\n\n🎭 动漫版：\n{anime_reply}")

@app.post("/api/ai-tools")
async def ai_tools(request: Request):
    data = await request.json()
    user_prompt = data.get("prompt", "")
    res = await weather(user_prompt)
    return {"response": f"AI处理结果: {res}"}