"""天气库的测试用例"""
import pytest
from weather_lib import parse_weather_data, is_comfortable, temp_category


# === 测试 parse_weather_data ===

def test_parse_normal_data():
    """测试正常的天气数据能正确解析"""
    fake_response = {
        "name": "Beijing",
        "sys": {"country": "CN"},
        "main": {"temp": 20.5, "feels_like": 19.0, "humidity": 50},
        "weather": [{"description": "晴"}],
        "wind": {"speed": 3.2}
    }
    
    result = parse_weather_data(fake_response)
    
    assert result["city"] == "Beijing"
    assert result["country"] == "CN"
    assert result["temp"] == 20.5
    assert result["humidity"] == 50
    assert result["description"] == "晴"


def test_parse_missing_field():
    """测试缺字段时会抛 KeyError"""
    bad_response = {"name": "Beijing"}
    
    with pytest.raises(KeyError):
        parse_weather_data(bad_response)


# === 测试 is_comfortable ===

def test_comfortable_perfect_weather():
    """完美天气应该是舒适的"""
    weather = {"temp": 22, "humidity": 50}
    assert is_comfortable(weather) is True


def test_comfortable_too_hot():
    """太热不舒适"""
    weather = {"temp": 35, "humidity": 50}
    assert is_comfortable(weather) is False


def test_comfortable_too_cold():
    """太冷不舒适"""
    weather = {"temp": 5, "humidity": 50}
    assert is_comfortable(weather) is False


def test_comfortable_humidity_too_low():
    """湿度太低不舒适"""
    weather = {"temp": 22, "humidity": 15}
    assert is_comfortable(weather) is False


def test_comfortable_boundary_values():
    """边界值测试: 18°C 和 26°C 应该都算舒适"""
    assert is_comfortable({"temp": 18, "humidity": 50}) is True
    assert is_comfortable({"temp": 26, "humidity": 50}) is True
    assert is_comfortable({"temp": 17.9, "humidity": 50}) is False
    assert is_comfortable({"temp": 26.1, "humidity": 50}) is False


# === 测试 temp_category（用参数化简化）===

@pytest.mark.parametrize("temp,expected", [
    (-5, "严寒"),
    (0, "寒冷"),
    (5, "寒冷"),
    (15, "凉爽"),
    (22, "舒适"),
    (30, "炎热"),
])
def test_temp_category(temp, expected):
    """一次测试多组输入"""
    assert temp_category(temp) == expected

@pytest.mark.parametrize("weather,expected",[
    ({"temp": 22, "humidity": 50}, True),   # 完美天气
    ({"temp": 35, "humidity": 50}, False),
])

def test_is_comfortable(weather,expected):
    assert is_comfortable(weather) == expected
    