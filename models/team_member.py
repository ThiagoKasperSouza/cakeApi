import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class TeamMemberStatus(str, enum.Enum):
    active = "active"
    inactive = "inactive"
    on_leave = "on_leave"


class TeamMember(Base):
    __tablename__ = "team_members"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[str] = mapped_column(String(120), nullable=False)
    email_address: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[TeamMemberStatus] = mapped_column(
        Enum(TeamMemberStatus, name="team_member_status"),
        default=TeamMemberStatus.active,
        nullable=False,
    )
    initials: Mapped[str | None] = mapped_column(String(10), nullable=True)
    color: Mapped[str | None] = mapped_column(String(20), nullable=True)
