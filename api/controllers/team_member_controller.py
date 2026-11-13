from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.dtos.team_member_dto import TeamMemberCreate, TeamMemberUpdate
from database.connection import get_db
from models.team_member import TeamMember, TeamMemberStatus
from services.team_member_service import TeamMemberService


class TeamMemberController:
    def __init__(
        self,
        service: TeamMemberService = Depends(),
        db: Session = Depends(get_db),
    ) -> None:
        self.service = service
        self.db = db

    def list_team_members(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: TeamMemberStatus | None = None,
    ) -> list[TeamMember]:
        return self.service.list_team_members(skip=skip, limit=limit, status=status_filter)

    def get_team_member(self, member_id: int) -> TeamMember:
        member = self.service.get_team_member(member_id)
        if member is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Membro não encontrado")
        return member

    def create_team_member(self, data: TeamMemberCreate) -> TeamMember:
        try:
            return self.service.create_team_member(data)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "E-mail já cadastrado") from None

    def update_team_member(self, member_id: int, data: TeamMemberUpdate) -> TeamMember:
        member = self.get_team_member(member_id)
        try:
            return self.service.update_team_member(member, data)
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(status.HTTP_409_CONFLICT, "E-mail já cadastrado") from None

    def delete_team_member(self, member_id: int) -> None:
        self.service.delete_team_member(self.get_team_member(member_id))
