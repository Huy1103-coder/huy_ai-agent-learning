from fastapi import FastAPI,HTTPException
from pydantic import BaseModel,Field

app = FastAPI(
    title="文本统计 API",
    description="接收一段文本,返回字符数、词数、行数等统计",
    version="1.0.0",
)


class TextRequest(BaseModel):
    
    text:str = Field(...,description="要分析的文本",min_length=1)
    language:str = Field("zh",description = "语言代码，如zh 或 en")


class TextStats(BaseModel):

    char_count:int = Field(...,description="字数总数（含空格）")
    char_count_no_space: int = Field(...,description="字数（不含空格）")
    word_count:int = Field(...,description = "词数")
    line_count: int = Field(..., description="行数")
    language: str = Field(..., description="使用的语言")


@app.get("/")
def read_root():
    """欢迎页"""
    return {
        "message": "欢迎使用文本统计 API",
        "docs": "/docs",
        "version": "1.0.0",
    }
    

@app.post("/text/analyze")
def analyze_text(request: TextRequest) -> TextStats:
    """
    分析一段文本,返回各种统计信息。
    
    支持中英文:中文按字符数,英文按空格切词。
    """
    text = request.text
    
    # 字符统计
    char_count = len(text)
    char_count_no_space = len(text.replace(" ", "").replace("\t", "").replace("\n", ""))
    
    # 词数统计
    if request.language == "zh":
        # 中文:简单按非空白字符算"词"
        # (真实场景需要分词库,这里简化)
        word_count = char_count_no_space
    else:
        # 英文:按空格切
        word_count = len(text.split())
    
    # 行数统计
    line_count = len(text.splitlines()) if text else 0
    
    return TextStats(
        char_count=char_count,
        char_count_no_space=char_count_no_space,
        word_count=word_count,
        line_count=line_count,
        language=request.language,
    )

@app.post("/text/uppercase")
def to_uppercase(request: TextRequest):

    return {"original":request.text,"result":request.text.upper()}

