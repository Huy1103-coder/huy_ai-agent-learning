from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv
from weather_lib import fetch_weather,is_comfortable, temp_category

load_dotenv()
API_KEY = os.getenv("OPENWEATHER_API_KEY")

app = FastAPI(
    title="天气查询 API",
    description="基于 OpenWeatherMap 的天气查询服务,带舒适度判断",
    version="1.0.0"
)


@app.get("/")
def read_root():
    return {
        "message": "天气查询 API",
        "usage": "访问 /weather/{城市英文名} 查询天气",
        "examples": [
            "/weather/Beijing",
            "/weather/Shanghai",
            "/weather/Tokyo",
        ],
        "docs": "/docs",
    }

@app.get("/weather/{city}")
def get_weather(city: str):
    """
    查询某个城市的天气,返回结构化数据。
    
    - **city**: 城市英文名,如 Beijing、Tokyo、London
    
    返回包含温度、湿度、天气描述,以及自动判断的舒适度和温度分类。
    """
    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="服务器未配置 API Key,请联系管理员"
        )
    
    weather = fetch_weather(city, API_KEY)
    
    if weather is None:
        raise HTTPException(
            status_code=404,
            detail=f"无法获取 '{city}' 的天气,请检查城市名是否正确"
        )
    
    # 加上舒适度和温度分类信息
    weather["is_comfortable"] = is_comfortable(weather)
    weather["temp_category"] = temp_category(weather["temp"])
    
    return weather


@app.get("/weather/{city}/comfortable")
def is_city_comfortable(city: str):
    """简化接口:只返回这个城市天气是否舒适"""
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API Key 未配置")
    
    weather = fetch_weather(city, API_KEY)
    if weather is None:
        raise HTTPException(status_code=404, detail=f"找不到城市 {city}")
    
    return {
        "city": weather["city"],
        "is_comfortable": is_comfortable(weather),
        "temp": weather["temp"],
        "description": weather["description"],
    }