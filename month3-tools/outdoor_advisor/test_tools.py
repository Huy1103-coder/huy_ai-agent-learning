"""
test_tools.py - 工具函数的单元测试

测试覆盖:
1. 正常路径(查到数据)
2. 失败路径(城市不存在 → error 字段)
3. 字段命名(必须有单位后缀)
"""

import pytest
from tools import get_weather, get_aqi


# ============================================================
# get_weather 测试
# ============================================================

def test_get_weather_returns_dict():
    """工具必须永远返回 dict(无论成功失败)"""
    result = get_weather("Beijing")
    assert isinstance(result, dict)


def test_get_weather_success_has_required_fields():
    """成功时,必须包含所有约定字段"""
    result = get_weather("Beijing")
    
    # 跳过测试如果 API 暂时不可用
    if "error" in result:
        pytest.skip(f"API 不可用: {result['error']}")
    
    required_fields = {
        "city",
        "temp_celsius",
        "feels_like_celsius",
        "humidity_percent",
        "description",
        "wind_speed_ms",
        "wind_speed_kmh",
    }
    assert required_fields.issubset(set(result.keys()))


def test_get_weather_field_units_in_names():
    """所有数值字段都必须带单位后缀(单元 28 工程化)"""
    result = get_weather("Beijing")
    if "error" in result:
        pytest.skip("API 不可用")
    
    # 温度字段必须以 _celsius 结尾
    assert "temp_celsius" in result
    assert "feels_like_celsius" in result
    
    # 风速字段必须带单位
    assert "wind_speed_ms" in result
    assert "wind_speed_kmh" in result


def test_get_weather_unknown_city_returns_error():
    """未知城市必须返回 error 字段,不能崩溃"""
    result = get_weather("AKjsdf12NotARealCity")
    assert "error" in result
    assert isinstance(result["error"], str)


def test_get_weather_wind_speed_unit_consistency():
    """wind_speed_kmh 必须等于 wind_speed_ms * 3.6(±0.5 容差)"""
    result = get_weather("Beijing")
    if "error" in result:
        pytest.skip("API 不可用")
    
    expected_kmh = result["wind_speed_ms"] * 3.6
    assert abs(result["wind_speed_kmh"] - expected_kmh) < 0.5


# ============================================================
# get_aqi 测试
# ============================================================

def test_get_aqi_returns_dict():
    result = get_aqi("Beijing")
    assert isinstance(result, dict)


def test_get_aqi_success_has_required_fields():
    result = get_aqi("Beijing")
    if "error" in result:
        pytest.skip(f"API 不可用: {result['error']}")
    
    required_fields = {
        "city",
        "aqi_level",
        "aqi_label",
        "pm2_5_ugm3",
        "pm10_ugm3",
    }
    assert required_fields.issubset(set(result.keys()))


def test_get_aqi_level_in_valid_range():
    """AQI 等级必须在 1-5"""
    result = get_aqi("Beijing")
    if "error" in result:
        pytest.skip("API 不可用")
    assert 1 <= result["aqi_level"] <= 5


def test_get_aqi_label_matches_level():
    """label 必须和 level 对应"""
    result = get_aqi("Beijing")
    if "error" in result:
        pytest.skip("API 不可用")
    
    expected_labels = {1: "优", 2: "良", 3: "中等", 4: "差", 5: "很差"}
    assert result["aqi_label"] == expected_labels[result["aqi_level"]]


def test_get_aqi_unknown_city_returns_error():
    """未知城市必须 error,不崩溃"""
    result = get_aqi("AKjsdf12NotARealCity")
    assert "error" in result