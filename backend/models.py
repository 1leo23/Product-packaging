from pydantic import BaseModel, Field, validator
import re

### 會員 (Member) 模型 ###
class Member(BaseModel):
    id: str = Field(..., min_length=10, max_length=10, description="請輸入有效身份證字號")
    sex: str = Field(..., description="請輸入 M 或 F")
    name: str = Field(..., min_length=1, description="姓名不能為空")
    yyyy: int = Field(..., description="出生年 (西元)")
    mm: int = Field(..., ge=1, le=12, description="出生月 (1-12)")
    dd: int = Field(..., ge=1, le=31, description="出生日 (1-31)")

    @validator("id")
    def validate_id(cls, value):
        if not re.match(r"^[A-Z][0-9]{9}$", value):
            raise ValueError("身份證字號格式錯誤 (應為 1 個大寫字母 + 9 個數字)")
        return value

    @validator("sex")
    def validate_sex(cls, value):
        if value not in ["M", "F"]:
            raise ValueError("性別只能是 'M' 或 'F'")
        return value

### 管理員 (Manager) 模型 ###
class Manager(BaseModel):
    id: str = Field(..., min_length=5, max_length=20, description="醫生個人編號")
    password: str = Field(..., min_length=6, description="密碼至少 6 碼")
    department: str = Field(..., description="醫生的科別")
    name: str = Field(..., min_length=1, description="姓名不能為空")
    numMembers: int = Field(default=0, description="患者人數")

### 登入請求模型 ###
class LoginRequest(BaseModel):
    id: str
    password: str

### 會員查詢模型 ###
class MemberQuery(BaseModel):
    id: str
