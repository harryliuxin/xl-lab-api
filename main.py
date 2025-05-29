from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import os
import requests
import calendar
from datetime import datetime

# 配置参数
API_KEY = "4b412cd28c1a4b50adb184728252905"
CITY = "Lijiang,China"
# 选择需要查看的年份（2020, 2021, 2022, 2023, 2024, 2025）
START_YEAR = 2020
END_YEAR = 2022
# 选择需要产看的月份
MONTH = 11

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["https://www.weixin.qq.com"],
    allow_origins=["*"],
    allow_methods=["GET", "POST", "OPTIONS"],  # 微信小程序会先发送 OPTIONS 预检请求
    allow_headers=["*"]
)

weatherCodes = {
    "113": "晴天",
    "116": "局部多云",
    "119": "多云",
    "122": "阴天",
    "143": "薄雾",
    "176": "周边有零星小雨",
    "179": "周边有零星小雪",
    "182": "周边有零星小雨夹雪",
    "185": "周边有有零星小冻雾雨",
    "200": "周边有雷雨",
    "227": "飞雪",
    "230": "暴风雪",
    "248": "雾",
    "260": "冻雾",
    "263": "零星细雨",
    "266": "细雨",
    "281": "冻雾雨",
    "284": "大冻雾雨",
    "293": "片状小雨",
    "296": "小雨",
    "299": "偶尔有中雨",
    "302": "中雨",
    "305": "偶尔有大雨",
    "308": "大雨",
    "311": "微冻雨",
    "314": "中到大冻雨",
    "317": "小雨夹雪",
    "320": "中到大雨夹雪",
    "323": "局部小雪",
    "326": "小雪",
    "329": "局部中雪",
    "332": "中雪",
    "335": "局部大雪",
    "338": "大雪",
    "350": "冰粒",
    "353": "小阵雨",
    "356": "中到大阵雨",
    "359": "暴雨阵雨",
    "362": "小雨夹雪阵雨",
    "365": "中到大雨夹雪阵雨",
    "368": "小雪阵雪",
    "371": "中到大雪阵雪",
    "374": "小阵冰粒",
    "377": "中到大阵冰粒",
    "386": "局部雷雨",
    "389": "中到大雷雨",
    "392": "局部雷雪",
    "395": "中到大雷雪",
}

def get_historical_weather():
    all_data = []
    
    for year in range(START_YEAR, END_YEAR + 1):
        url = f"http://api.worldweatheronline.com/premium/v1/past-weather.ashx"
        _, last_day = calendar.monthrange(year, MONTH)
        params = {
            "key": API_KEY,
            "q": CITY,
            "date": f"{year}-{MONTH:02d}-01",
            "enddate": f"{year}-{MONTH:02d}-{last_day}",
            "tp": 24,
            "format": "json"
        }
        response = requests.get(url, params=params)
        data = response.json()
        for day in data["data"]["weather"]:
            date_str = day["date"]
            sunrise = day["astronomy"][0]["sunrise"]
            sunset = day["astronomy"][0]["sunset"]
            max_temp = int(day["maxtempC"])
            min_temp = int(day["mintempC"])
            weatherCode = day["hourly"][0]["weatherCode"]
            weather = weatherCodes[weatherCode]
            icon = day["hourly"][0]["weatherIconUrl"][0]["value"]
            all_data.append({
                "year": year,
                "date": datetime.strptime(date_str, "%Y-%m-%d"),
                "sunrise": sunrise,
                "sunset": sunset,
                "max_temp": max_temp,
                "min_temp": min_temp,
                "weather": weather,
                "icon": icon
            })
    
    return all_data

# # 获取并处理数据
# df = get_historical_weather()

# # 计算平均温度
# df["avg_temp"] = (df["max_temp"] + df["min_temp"]) / 2

# # 按年份分组统计
# summary = df.groupby("year").agg({
#     "avg_temp": ["mean", "min", "max"],
#     "condition": lambda x: x.mode()[0]  # 最常见天气
# }).reset_index()

# # 重命名列
# summary.columns = ["year", "avg_temp", "min_temp", "max_temp", "most_common_weather"]

    
# async def weather(city: str):
#     weather_data = get_historical_weather(city)
#     if "error" in weather_data:
#         return(f"❌ 获取天气失败: {weather_data['error']}")
#     else:
#         basic_info = (
#             f"🌆 {city}天气：\n"
#             f"🌡️ 温度: {weather_data['temp']}°C\n"
#             f"📝 描述: {weather_data['description']}\n"
#             f"💧 湿度: {weather_data['humidity']}%"
#         )
#         anime_reply = generate_anime_weather(city, weather_data)
#         return (f"{basic_info}\n\n🎭 动漫版：\n{anime_reply}")

@app.post("/api/ai-tools")
async def ai_tools(request: Request):
    data = await request.json()
    user_prompt = data.get("prompt", "")
    res = await get_historical_weather()
    return {"response": f"AI处理结果: {res}"}