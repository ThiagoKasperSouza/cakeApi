from pydantic import BaseModel, ConfigDict, EmailStr, Field

from models.team_member import TeamMemberStatus


class TeamMemberBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    role: str = Field(min_length=1, max_length=120)
    email_address: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    status: TeamMemberStatus = TeamMemberStatus.active
    initials: str | None = Field(default=None, max_length=10)
    color: str | None = Field(default=None, max_length=20)


class TeamMemberCreate(TeamMemberBase):
    pass


class TeamMemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    role: str | None = Field(default=None, min_length=1, max_length=120)
    email_address: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    status: TeamMemberStatus | None = None
    initials: str | None = Field(default=None, max_length=10)
    color: str | None = Field(default=None, max_length=20)


class TeamMemberRead(TeamMemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
