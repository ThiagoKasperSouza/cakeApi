from fastapi import APIRouter, Depends, status

from api.controllers.team_member_controller import TeamMemberController
from api.dtos.team_member_dto import TeamMemberCreate, TeamMemberRead, TeamMemberUpdate
from models.team_member import TeamMemberStatus

router = APIRouter(prefix="/team-members", tags=["team-members"])


@router.get("", response_model=list[TeamMemberRead])
def list_team_members(
    skip: int = 0,
    limit: int = 100,
    status_filter: TeamMemberStatus | None = None,
    controller: TeamMemberController = Depends(),
):
    return controller.list_team_members(skip=skip, limit=limit, status_filter=status_filter)


@router.get("/{member_id}", response_model=TeamMemberRead)
def get_team_member(member_id: int, controller: TeamMemberController = Depends()):
    return controller.get_team_member(member_id)


@router.post("", response_model=TeamMemberRead, status_code=status.HTTP_201_CREATED)
def create_team_member(data: TeamMemberCreate, controller: TeamMemberController = Depends()):
    return controller.create_team_member(data)


@router.patch("/{member_id}", response_model=TeamMemberRead)
def update_team_member(member_id: int, data: TeamMemberUpdate, controller: TeamMemberController = Depends()):
    return controller.update_team_member(member_id, data)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team_member(member_id: int, controller: TeamMemberController = Depends()):
    controller.delete_team_member(member_id)
