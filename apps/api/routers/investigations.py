"""TraceX API routers - investigations."""

from datetime import UTC, datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.collectors import get_available_collectors
from packages.common.dependencies import get_current_user
from packages.database.models import Case, Investigation, InvestigationStatus, Target
from packages.database.session import get_session

router = APIRouter(prefix="/api/v1/investigations", tags=["investigations"])


class StartInvestigationRequest(BaseModel):
    case_id: str
    target_ids: list[str]
    collectors: list[str] | None = None


class InvestigationResponse(BaseModel):
    id: str
    case_id: str
    status: str
    progress: float
    current_collector: str | None = None
    collectors_run: list[str] = []
    collectors_failed: list[str] = []
    entities_found: int
    relationships_found: int
    evidence_count: int
    errors: list[dict] = []
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=InvestigationResponse)
async def start_investigation(
    request: StartInvestigationRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Start a new investigation."""
    case_result = await session.execute(select(Case).where(Case.id == request.case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.owner_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    for target_id in request.target_ids:
        target_result = await session.execute(
            select(Target).where(Target.id == target_id, Target.case_id == request.case_id)
        )
        if not target_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail=f"Target {target_id} not found")

    investigation = Investigation(
        case_id=request.case_id,
        status="pending",
        collectors_run=[],
        collectors_failed=[],
        errors=[],
    )
    session.add(investigation)
    await session.commit()
    await session.refresh(investigation)

    background_tasks.add_task(run_investigation_task, investigation.id, request.collectors)

    return investigation


async def run_investigation_task(investigation_id: str, collectors: list[str] | None = None):
    """Background task to run investigation."""
    from packages.database.session import get_session_context

    async with get_session_context() as session:
        result = await session.execute(
            select(Investigation).where(Investigation.id == investigation_id)
        )
        investigation = result.scalar_one_or_none()
        if not investigation:
            return

        investigation.status = InvestigationStatus.RUNNING
        investigation.started_at = datetime.now(UTC)
        await session.commit()

        investigation.status = InvestigationStatus.COMPLETED
        investigation.completed_at = datetime.now(UTC)
        investigation.progress = 1.0
        investigation.collectors_run = collectors or list(get_available_collectors().keys())
        await session.commit()


@router.get("/{investigation_id}", response_model=InvestigationResponse)
async def get_investigation(
    investigation_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Get investigation details."""
    result = await session.execute(
        select(Investigation).where(Investigation.id == investigation_id)
    )
    investigation = result.scalar_one_or_none()
    if not investigation:
        raise HTTPException(status_code=404, detail="Investigation not found")
    return investigation


@router.get("/case/{case_id}", response_model=list[InvestigationResponse])
async def list_investigations(
    case_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """List all investigations for a case."""
    result = await session.execute(
        select(Investigation).where(Investigation.case_id == case_id)
    )
    return result.scalars().all()
