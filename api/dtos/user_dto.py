from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email_address: EmailStr


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    email_address: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool


class ChangePassword(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email_address: EmailStr
    password: str
