"""
AI 简历信息提取器
输入:自由格式的简历文本
输出:结构化的 JSON 候选人信息(经 Pydantic 校验)
"""
import os
import json
from pathlib import Path
from typing import Optional
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError, EmailStr
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)


# ==========================================
# 第 1 部分:数据模型(Pydantic Schema)
# ==========================================

class Education(BaseModel):
    """单条教育经历"""
    school: str = Field(..., description="学校名称")
    major: Optional[str] = Field(None, description="专业")
    degree: Optional[str] = Field(None, description="学历(本科/硕士/博士)")
    start_year: Optional[int] = Field(None, description="入学年份")
    end_year: Optional[int] = Field(None, description="毕业年份")


class WorkExperience(BaseModel):
    """单条工作经历"""
    company: str = Field(..., description="公司名称")
    position: str = Field(..., description="职位")
    start_year: Optional[int] = Field(None, description="入职年份")
    end_year: Optional[int] = Field(None, description="离职年份,在职可填 null")
    description: Optional[str] = Field(None, description="主要职责或成就(一句话)")


class Resume(BaseModel):
    """完整简历结构"""
    name: str = Field(..., description="候选人姓名")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, description="电话")
    location: Optional[str] = Field(None, description="现居城市")
    years_of_experience: Optional[int] = Field(None, description="工作年限(年)", ge=0)
    education: list[Education] = Field(default_factory=list, description="教育经历列表")
    work_experience: list[WorkExperience] = Field(default_factory=list, description="工作经历列表")
    skills: list[str] = Field(default_factory=list, description="技能列表")


# ==========================================
# 第 2 部分:提取函数
# ==========================================

SYSTEM_PROMPT = """你是一名专业的简历解析助手。从用户提供的简历文本中提取关键信息,
返回严格的 JSON 格式。

# 必须包含的字段
- name: 候选人姓名(必填)
- email: 邮箱(没有就 null)
- phone: 电话(没有就 null)
- location: 现居城市(没有就 null)
- years_of_experience: 工作年限,数字(没有信息就 null)
- education: 教育经历数组,每条含 school/major/degree/start_year/end_year
- work_experience: 工作经历数组,每条含 company/position/start_year/end_year/description
- skills: 技能字符串数组

# 规则
- 时间字段必须是 4 位数字年份(如 2019),不是月份不是字符串
- degree 字段标准化为:本科 / 硕士 / 博士 / 大专 / 高中
- 没找到的字段用 null 或空数组,**不要编造**
- description 控制在 30 字以内,提炼主要职责或成就
- 如果原文没明确写入学年份,start_year 必须为 null

# 示例输出格式
{
  "name": "张明",
  "email": "zhang@example.com",
  "phone": "13800138000",
  "location": "北京",
  "years_of_experience": 5,
  "education": [{"school": "清华大学", "major": "计算机", "degree": "本科", "start_year": 2015, "end_year": 2019}],
  "work_experience": [{"company": "字节跳动", "position": "工程师", "start_year": 2019, "end_year": 2023, "description": "负责推荐系统"}],
  "skills": ["Python", "MySQL", "英语"]
}"""


def extract_resume(text: str) -> Optional[Resume]:
    """
    从简历文本中提取结构化信息。
    返回 Resume 对象,失败返回 None。
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        print(f"❌ API 调用失败:{e}")
        return None
    
    raw_json = response.choices[0].message.content
    
    # 解析 JSON
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败:{e}")
        print(f"   原始输出:{raw_json[:200]}...")
        return None
    
    # Pydantic 校验
    try:
        resume = Resume(**data)
        return resume
    except ValidationError as e:
        print(f"❌ 数据校验失败:")
        for err in e.errors():
            print(f"   字段 {err['loc']}:{err['msg']}")
        return None


# ==========================================
# 第 3 部分:友好展示函数
# ==========================================

def display_resume(resume: Resume) -> None:
    """把简历对象漂亮地打印出来"""
    print("\n" + "=" * 60)
    print(f"📋 候选人:{resume.name}")
    print("=" * 60)
    
    # 基础信息
    if resume.email:
        print(f"📧 邮箱:{resume.email}")
    if resume.phone:
        print(f"📱 电话:{resume.phone}")
    if resume.location:
        print(f"📍 现居:{resume.location}")
    if resume.years_of_experience is not None:
        print(f"💼 工作年限:{resume.years_of_experience} 年")
    
    # 教育
    if resume.education:
        print(f"\n🎓 教育经历:")
        for edu in resume.education:
            period = f"{edu.start_year}-{edu.end_year}" if edu.start_year and edu.end_year else ""
            line = f"  • {edu.school}"
            if edu.major:
                line += f" | {edu.major}"
            if edu.degree:
                line += f" | {edu.degree}"
            if period:
                line += f" ({period})"
            print(line)
    
    # 工作
    if resume.work_experience:
        print(f"\n💼 工作经历:")
        for w in resume.work_experience:
            period = f"{w.start_year}-{w.end_year if w.end_year else '至今'}"
            print(f"  • {w.company} | {w.position} ({period})")
            if w.description:
                print(f"    {w.description}")
    
    # 技能
    if resume.skills:
        print(f"\n🛠 技能:{', '.join(resume.skills)}")


# ==========================================
# 第 4 部分:测试样本
# ==========================================

test_resumes = [
    # 样本 1:相对完整的简历
    """
张明
联系方式:zhang@example.com / 13800138000
现居:北京

教育背景:
2015.9 - 2019.6  清华大学  计算机科学与技术  本科

工作经历:
2019.7 - 2023.5  字节跳动  Python 后端工程师
负责推荐系统的后端服务开发,日活 1000 万 + 用户。

2023.6 - 至今    腾讯  高级后端工程师
微信支付核心交易链路开发。

技能:Python, Django, FastAPI, MySQL, Redis, Docker, Kubernetes, 英语 CET-6
""",
    
    # 样本 2:简短风格
    """
李华,前端工程师,5 年经验。
邮箱 lihua@gmail.com,在上海。
浙江大学软件工程毕业,2018 届。
做过阿里、美团。会 React、Vue、TypeScript。
""",
    
    # 样本 3:描述很自然
    """
我叫王芳,刚刚从北京大学经济学硕士毕业(2024)。
之前在 2020-2024 期间在大学读硕士前,我先在 2015-2019 在复旦读了本科。
本科期间在德勤实习过 2 年。会数据分析、Python、SQL、Excel、英语流利。
邮箱:wangfang@pku.edu.cn
""",
    
    # 样本 4:故意残缺
    """
小李,会编程,想找工作。
""",
]


# ==========================================
# 第 5 部分:主流程
# ==========================================

if __name__ == "__main__":
    for i, text in enumerate(test_resumes, 1):
        print("\n" + "█" * 60)
        print(f"测试 {i}")
        print("█" * 60)
        print(f"原始简历:\n{text}")
        
        resume = extract_resume(text)
        
        if resume:
            display_resume(resume)
        else:
            print("⚠️ 提取失败,需要人工审核")