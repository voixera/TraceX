"""TraceX API routers - investigations."""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from packages.database.session import get_session
from packages.database.models import Investigation, Case, Target, InvestigationStatus
from packages.models.schemas import Investigation as InvestigationSchema
from packages.common.dependencies import get_current_user
from packages.core.engine import IntelligenceEngine
from packages.collectors import get_available_collectors

router = APIRouter(prefix="/api/v1/investigations", tags=["investigations"])


class StartInvestigationRequest(BaseModel):
    case_id: str
    target_ids: List[str]
    collectors: Optional[List[str]] = None


@router.post("/", response_model=InvestigationSchema)
async def start_investigation(
    request: StartInvestigationRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Start a new investigation."""
    # Verify case exists and user owns it
    case_result = await session.execute(select(Case).where(Case.id == request.case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.owner_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    # Verify targets exist
    targets = []
    for target_id in request.target_ids:
        target_result = await session.execute(
            select(Target).where(Target.id == target_id, Target.case_id == request.case_id)
        )
        target = target_result.scalar_one_or_none()
        if not target:
            raise HTTPException(status_code=404, detail=f"Target {target_id} not found")
        targets.append(target)

    # Create investigation
    investigation = Investigation(
        case_id=request.case_id,
        status=InvestigationStatus.PENDING,
        collectors_run=[],
        collectors_failed=[],
        errors=[],
    )
    session.add(investigation)
    await session.commit()
    await session.refresh(investigation)

    # Schedule background task
    background_tasks.add_task(run_investigation_task, investigation.id, request.collectors)

    return investigation


async def run_investigation_task(investigation_id: str, collectors: Optional[List[str]] = None):
    """Background task to run investigation."""
    from datetime import datetime, timezone
    from packages.database.session import get_session_context
    from packages.database.models import Investigation, InvestigationStatus

    async with get_session_context() as session:
        result = await session.execute(
            select(Investigation).where(Investigation.id == investigation_id)
        )
        investigation = result.scalar_one_or_none()
        if not investigation:
            return

        investigation.status = InvestigationStatus.RUNNING
        investigation.started_at = datetime.now(timezone.utc)
        await session.commit()

        # Run collectors (simplified - full implementation would use the engine)
        investigation.status = InvestigationStatus.COMPLETED
        investigation.completed_at = datetime.now(timezone.utc)
        investigation.progress = 1.0
        investigation.collectors_run = collectors or list(get_available_collectors().keys())
        await session.commit()


@router.get("/{investigation_id}", response_model=InvestigationSchema)
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


@router.get("/case/{case_id}", response_model=List[InvestigationSchema])
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