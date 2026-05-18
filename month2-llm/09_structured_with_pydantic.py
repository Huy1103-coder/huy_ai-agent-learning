import os
import json
from pathlib import Path
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel,Field,ValidationError
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent /".env"
load_dotenv(env_path)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

class ProductInfo(BaseModel):
    product: str = Field(...,description = "产品名称")
    price: float = Field(...,description = "价格（人民币）",gt =0)
    colors:list[str] = Field(default_factory= list,description="可选颜色列表")
    sizes: list[str] = Field(default=list, description= "可选尺码列表")
    in_stock:bool = Field(True, description="是否有库存")


def extract_product_info(text:str) -> Optional[ProductInfo]:
    """
    从自由文本中提取产品信息。
    返回 ProductInfo 对象,失败时返回 None
    """
    response = client.chat.completions.create(
       model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": """你是一个商品信息提取助手。从用户提供的商品描述中提取关键信息,
返回严格的 JSON 格式,包含以下字段:
- product: 产品名称(字符串)
- price: 价格(数字,人民币)
- colors: 可选颜色列表(字符串数组)
- sizes: 可选尺码列表(字符串数组)
- in_stock: 是否有库存(布尔值)

如果文本中没有提到某个字段,该字段可省略或用默认值:
- colors/sizes 默认空数组 []
- in_stock 默认 true"""
            },
            {"role": "user", "content": text},
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw_json = response.choices[0].message.content

    try:
        data = json.loads(raw_json)
    except json.JASONDecodeError as e:
        print()
        print(f"❌ JSON 解析失败:{e}")
        print(f"   原始输出:{raw_json}")
        return None
    
    try:
        product = ProductInfo(**data)
        return product
    except ValidationError as e:
        print(f"❌ Pydantic 校验失败:")
        for err in e.errors():
            print(f"   字段 {err['loc']}:{err['msg']}")
        return None
    

test_cases = [
    "这件连衣裙现价 199 元,有红色、黑色、白色三种颜色,尺码 S/M/L 都有",
    "夏季短袖 T 恤,89 块,纯白和浅蓝两个颜色可选",
    "牛仔裤 250 元,目前缺货中,等返货",
    "这件衣服很漂亮",   # 故意残缺,测试错误处理
]


for i,text in enumerate(test_cases,1):
    print("="*60)
    print(f"测试{i}:{text}")
    print("="*60)

    result = extract_product_info(text)

    if result:
        print(f"✅ 提取成功:")
        print(f"   产品:{result.product}")
        print(f"   价格:¥{result.price}")
        print(f"   颜色:{result.colors}")
        print(f"   尺码:{result.sizes}")
        print(f"   有货:{result.in_stock}")
    else:
        print("⚠️ 提取失败,需人工处理")
    print()