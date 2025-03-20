import uuid
from typing import Optional
from pydantic import BaseModel, Field


class Member(BaseModel):
    account: str = Field(max_length=16,
                         min_length=8, description='最少輸入8個字元,最多16個字元')
    password: str = Field(...)
    name: str = Field(...)
    phone: str = Field(...)
    '''
    Field(...)是必填欄位,Field（None） 是可選填
    Field(None,title="The description of the item",max_length=10,alias='我是替代字')

    '''

    class Config:
        allow_population_by_field_name = True
        schema_extra = {
            "example": {
                "account": "testtest123",
                "password": "testpassword",
                "name": "Ansel",
                "phone": "0912345678"
            }
        }


class MemberUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "name": "NewName",
                "phone": "0900123321"
            }
        }