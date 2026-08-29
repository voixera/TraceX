"""TraceX API routers - entities."""


from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.common.dependencies import get_current_user
from packages.database.models import Case, Entity
from packages.database.session import get_session

router = APIRouter(prefix="/api/v1/entities", tags=["entities"])


class EntityResponse(BaseModel):
    id: str
    case_id: str
    entity_type: str
    value: str
    name: str | None
    description: str | None
    confidence: float
    metadata: dict
    first_seen: str
    last_seen: str
    source_ids: list[str]

    class Config:
        from_attributes = True


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """Get entity details."""
    result = await session.execute(select(Entity).where(Entity.id == entity_id))
    entity = result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")
    return entity


@router.get("/case/{case_id}", response_model=list[EntityResponse])
async def list_entities(
    case_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: str = Depends(get_current_user),
):
    """List all entities in a case."""
    case_result = await session.execute(select(Case).where(Case.id == case_id))
    case = case_result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    if case.owner_id != current_user:
        raise HTTPException(status_code=403, detail="Access denied")

    result = await session.execute(select(Entity).where(Entity.case_id == case_id))
    return result.scalars().all()
