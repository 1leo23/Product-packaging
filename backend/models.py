from pydantic import BaseModel, Field, validator
import re
from typing import List, Optional
from datetime import datetime

### 會員 (Member) 模型 ###
class Member(BaseModel):
    id: str = Field(..., min_length=10, max_length=10, description="請輸入有效身份證字號")
    sex: str = Field(..., description="請輸入 M 或 F")
    name: str = Field(..., min_length=1, description="姓名不能為空")
    yyyy: int = Field(..., description="出生年 (西元)")
    mm: int = Field(..., ge=1, le=12, description="出生月 (1-12)")
    dd: int = Field(..., ge=1, le=31, description="出生日 (1-31)")
    profile_image_path: str = Field(..., description="會員的個人照路徑")
    password: Optional[str] = None  # 密碼預設為出生年月日

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

    def generate_password(self):
        """ 生成密碼：格式為 yyyyMMdd """
        self.password = f"{self.yyyy}{str(self.mm).zfill(2)}{str(self.dd).zfill(2)}"

### 管理員 (Manager) 模型 ###
class Manager(BaseModel):
    id: str = Field(..., min_length=5, max_length=20, description="醫生個人編號")
    password: str = Field(..., min_length=6, description="密碼至少 6 碼")
    department: str = Field(..., description="醫生的科別")
    name: str = Field(..., min_length=1, description="姓名不能為空")
    profile_image_path: str = Field(..., description="醫生的個人照路徑")
    numMembers: int = Field(default=0, description="患者人數")

### 登入請求模型 ###
class LoginRequest(BaseModel):
    id: str
    password: str

class ManagerToken(BaseModel):
    token: str

class MemberQuery(BaseModel):
    id: str

class UpdatePasswordRequest(BaseModel):
    id: str
    old_password: str
    new_password: str

class Record(BaseModel):
    member_id: str
    brain_age: Optional[int] = None
    actual_age: Optional[int] = None  # 讓 actual_age 自動計算
    date: str = Field(..., description="請輸入日期 (YYYY-MM-DD)")
    image_path: str
    risk_score: Optional[int] = 0

    @validator("date")
    def validate_and_format_date(cls, value):
        try:
            if len(value) == 8 and value.isdigit():
                return datetime.strptime(value, "%Y%m%d").strftime("%Y-%m-%d")
            datetime.strptime(value, "%Y-%m-%d")  # 檢查格式是否正確
            return value
        except ValueError:
            raise ValueError("日期格式錯誤，請輸入 'YYYY-MM-DD' 或 'YYYYMMDD'")

    def compute_actual_age(self, birthdate: str):
        """ 計算實際年齡 """
        birth_date = datetime.strptime(birthdate, "%Y-%m-%d").date()
        record_date = datetime.strptime(self.date, "%Y-%m-%d").date()
        actual_age = record_date.year - birth_date.year - (
            (record_date.month, record_date.day) < (birth_date.month, birth_date.day)
        )
        self.actual_age = actual_age


class MemberLoginResponse(BaseModel):
    member_token: str
    message: str

class ManagerLoginResponse(BaseModel):
    manager_token: str
    message: str