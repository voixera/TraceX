"""TraceX API routers - cases."""

from datetime import UTC

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.common.dependencies import get_current_user
from packages.database.models import Case, CaseStatus
from packages.database.session import get_session

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])


class CaseCreate(BaseModel):
    name: str
    description: str | None = None
    tags: list[str] = []


class CaseResponse(BaseModel):
    id: str
    name: str
    description: str | None
    status: str
    tags: list[str]
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.post("/", response_model=CaseResponse)
async def create_case(
    case_data: CaseCreate,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Create a new investigation case."""
    case = Case(
        name=case_data.name,
        description=case_data.description,
        owner_id=current_user,
        status="active",
        tags=case_data.tags,
    )
    session.add(case)
    await session.commit()
    await session.refresh(case)
    return case


@router.get("/", response_model=list[CaseResponse])
async def list_cases(
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """List all investigation cases."""
    result = await session.execute(select(Case).where(Case.owner_id == current_user))
    cases = result.scalars().all()
    return cases


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Get case details."""
    result = await session.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.owner_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")
    return case


@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: str,
    case_data: CaseCreate,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Update a case."""
    result = await session.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.owner_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    case.name = case_data.name
    case.description = case_data.description
    case.tags = case_data.tags

    await session.commit()
    await session.refresh(case)
    return case


@router.delete("/{case_id}")
async def delete_case(
    case_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Delete a case."""
    result = await session.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.owner_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    case.status = CaseStatus.DELETED
    await session.commit()
    return {"detail": "Case deleted"}


@router.post("/{case_id}/archive", response_model=CaseResponse)
async def archive_case(
    case_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Archive a case."""
    from datetime import datetime

    result = await session.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.owner_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    case.status = CaseStatus.ARCHIVED
    case.archived_at = datetime.now(UTC)
    await session.commit()
    await session.refresh(case)
    return case
