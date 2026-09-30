from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas.batch import BatchRead, BatchCreate
from src.core.dependencies import get_batch_service
from src.domain.exceptions import BatchAlreadyExistsError
from src.domain.services.batch_service import BatchService

router = APIRouter(prefix="/batches", tags=["batches"])


@router.get("/{batch_id}", response_model=BatchRead)
async def get_batch(batch_id: int, service: BatchService = Depends(get_batch_service)):
    batch = await service.get_batch(batch_id)
    if batch is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return batch


@router.post("", status_code=201)
async def create_batches(
        items: list[BatchCreate],
        service: BatchService = Depends(get_batch_service),
) -> None:
    try:
        for item in items:
            await service.create_batch(**item.model_dump())
    except BatchAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
