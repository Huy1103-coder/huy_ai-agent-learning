
"""流式 + 错误处理"""
import os
from pathlib import Path
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


def safe_streaming_chat(question: str) -> str:
    """带错误处理的流式对话,返回完整回答"""
    full_text = ""
    
    try:
        stream = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": question}],
            stream=True,
        )
        
        for chunks in stream:
            try:
                if chunks.choices and chunks.choices[0].delta.content:
                    text = chunks.choices[0].delta.content
                    full_text += text
                    print(text, end="", flush=True)
            except Exception as e:
                # 单个 chunk 解析失败,不中断整个流
                print(f"\n⚠️ 解析 chunk 失败:{e}")
                continue
        
        return full_text
    
    except RateLimitError as e:
        print(f"\n❌ 限流:{e}")
        print("建议:等待一段时间后重试")
        return ""
    
    except APIConnectionError as e:
        print(f"\n❌ 网络错误:{e}")
        print("建议:检查网络")
        return ""
    
    except APIError as e:
        print(f"\n❌ API 错误:{e}")
        return ""
    
    except Exception as e:
        print(f"\n❌ 未知错误:{e}")
        return ""


if __name__ == "__main__":
    result = safe_streaming_chat("简单介绍 FastAPI")
    print(f"\n\n完整回答长度:{len(result)} 字")