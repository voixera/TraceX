"""TraceX API routers - targets."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from packages.database.session import get_session
from packages.database.models import Target, Case
from packages.common.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/targets", tags=["targets"])


class TargetCreate(BaseModel):
    case_id: str
    target_type: str
    value: str
    metadata: dict = {}


class TargetResponse(BaseModel):
    id: str
    case_id: str
    target_type: str
    value: str
    metadata: dict
    created_at: str

    class Config:
        from_attributes = True


@router.post("/", response_model=TargetResponse)
async def create_target(
    target: TargetCreate,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Add a target to a case."""
    case_result = await session.execute(select(Case).where(Case.id == target.case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.owner_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    db_target = Target(
        case_id=target.case_id,
        target_type=target.target_type,
        value=target.value,
        metadata=target.metadata,
    )
    session.add(db_target)
    await session.commit()
    await session.refresh(db_target)
    return db_target


@router.get("/case/{case_id}", response_model=List[TargetResponse])
async def list_targets(
    case_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """List all targets in a case."""
    case_result = await session.execute(select(Case).where(Case.id == case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.owner_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await session.execute(select(Target).where(Target.case_id == case_id))
    targets = result.scalars().all()
    return targets


@router.delete("/{target_id}")
async def delete_target(
    target_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Delete a target."""
    target_result = await session.execute(select(Target).where(Target.id == target_id))
    target = target_result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    case_result = await session.execute(select(Case).where(Case.id == target.case_id))
    case = case_result.scalar_one_or_none()
    if not case or case.owner_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    await session.delete(target)
    await session.commit()
    return {"detail": "Target deleted"}