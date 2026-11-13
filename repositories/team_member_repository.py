from sqlalchemy import select

from models.team_member import TeamMember, TeamMemberStatus
from repositories.base_repository import BaseRepository


class TeamMemberRepository(BaseRepository[TeamMember]):
    model = TeamMember

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TeamMemberStatus | None = None,
    ) -> list[TeamMember]:
        stmt = select(TeamMember)
        if status is not None:
            stmt = stmt.where(TeamMember.status == status)
        return list(self.db.scalars(stmt.offset(skip).limit(limit)).all())
