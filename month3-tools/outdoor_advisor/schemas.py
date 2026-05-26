"""
schemas.py - LLM 工具调用的 schema 定义

schema 和工具函数分离的好处:
1. 想换工具实现(mock → 真实)只动 tools.py,schema 不变
2. 想优化 description 只动 schemas.py,函数代码不变
3. 看 schemas.py 能一眼看出"Agent 能做什么"
"""

from prompts import CITY_PARAM_DESC


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": (
                "查询全球任意城市的实时天气。返回字段:"
                "temp_celsius(摄氏度),feels_like_celsius(体感摄氏度),"
                "humidity_percent(湿度百分比),description(天气描述),"
                "wind_speed_ms(风速 m/s),wind_speed_kmh(风速 km/h)。"
                "仅返回当前天气,不支持预报。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": CITY_PARAM_DESC,
                    },
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_aqi",
            "description": (
                "查询城市当前空气质量。返回字段:"
                "aqi_level(1-5,数字越大越差),aqi_label(中文等级:优/良/中等/差/很差),"
                "pm2_5_ugm3(PM2.5 浓度 μg/m³,大于 75 视为不健康),"
                "pm10_ugm3(PM10 浓度 μg/m³),"
                "co_ugm3(一氧化碳),no2_ugm3(二氧化氮)。"
                "用于判断是否适合户外活动。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": CITY_PARAM_DESC,
                    },
                },
                "required": ["city"],
            },
        },
    },
]