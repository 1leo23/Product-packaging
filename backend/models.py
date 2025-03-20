from pydantic import BaseModel, Field, validator
import re

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

class LoginRequest(BaseModel):
    id: str = Field(..., min_length=10, max_length=10)
    password: str

class MemberQuery(BaseModel):
    id: str = Field(..., min_length=10, max_length=10)

class UpdatePasswordRequest(BaseModel):
    id: str = Field(..., min_length=10, max_length=10)
    old_password: str
    new_password: str
