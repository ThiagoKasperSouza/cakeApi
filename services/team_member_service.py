from fastapi import Depends
from sqlalchemy.orm import Session

from api.dtos.team_member_dto import TeamMemberCreate, TeamMemberUpdate
from database.connection import get_db
from models.team_member import TeamMember, TeamMemberStatus
from repositories.team_member_repository import TeamMemberRepository


class TeamMemberService:
    def __init__(self, db: Session = Depends(get_db)) -> None:
        self.repository = TeamMemberRepository(db)

    def list_team_members(
        self,
        skip: int = 0,
        limit: int = 100,
        status: TeamMemberStatus | None = None,
    ) -> list[TeamMember]:
        return self.repository.list(skip=skip, limit=limit, status=status)

    def get_team_member(self, member_id: int) -> TeamMember | None:
        return self.repository.get(member_id)

    def create_team_member(self, data: TeamMemberCreate) -> TeamMember:
        return self.repository.add(TeamMember(**data.model_dump()))

    def update_team_member(self, member: TeamMember, data: TeamMemberUpdate) -> TeamMember:
        return self.repository.update(member, data.model_dump(exclude_unset=True))

    def delete_team_member(self, member: TeamMember) -> None:
        self.repository.delete(member)
