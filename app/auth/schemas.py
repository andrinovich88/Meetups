from typing import Optional, Union

from pydantic import (UUID4, BaseModel, EmailStr, Field, FutureDate,
                      StrictBool, StrictInt, StrictStr, validator)


class UserCreate(BaseModel):
    email: EmailStr
    username: StrictStr
    password: StrictStr
    first_name: StrictStr = None
    last_name:  StrictStr = None


class UserUpdate(BaseModel):
    email: EmailStr = None
    password: StrictStr = None
    last_name: StrictStr = None
    first_name: StrictStr = None


class UserBase(BaseModel):
    id: StrictInt
    email: EmailStr
    username: StrictStr
    is_super: StrictBool


class UserProfile(BaseModel):
    email:    EmailStr
    username: StrictStr
    id:       StrictInt
    is_super: StrictBool
    last_name:  Union[StrictStr, type(None)]
    avatar_url: Union[StrictStr, type(None)]
    first_name: Union[StrictStr, type(None)]


class SimpleMessage(BaseModel):
    success: StrictBool
    message: StrictStr


class TokenBase(BaseModel):
    expires: FutureDate
    token_type: Optional[StrictStr] = "bearer"
    token: UUID4 = Field(..., alias="access_token")

    class Config:
        allow_population_by_field_name = True

    @validator("token")
    def hexlify_token(cls, value):
        return value.hex


class User(UserBase):
    token: TokenBase
