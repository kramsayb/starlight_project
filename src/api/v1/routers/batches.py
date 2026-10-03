from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.v1.schemas.batch import BatchRead, BatchCreate, BatchUpdate
from src.core.dependencies import get_batch_service, get_product_service
from src.domain.exceptions import BatchAlreadyExistsError
from src.domain.services.batch_service import BatchService
from src.domain.services.product_service import ProductService
from src.api.v1.schemas.product import AggregateRequest, AggregateResult


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


@router.patch("/{batch_id}", response_model=BatchRead)
async def update_batch(
        batch_id: int,
        data: BatchUpdate,
        service: BatchService = Depends(get_batch_service),
):
    fields = data.model_dump(exclude_unset=True)
    is_closed = fields.pop("is_closed", None)
    result = await service.update_batch(batch_id, is_closed=is_closed, **fields)
    if result is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return result


@router.get("", response_model=list[BatchRead])
async def list_batches(
        is_closed: bool | None = None,
        batch_number: int | None = None,
        batch_date: date | None = None,
        work_center_id: int | None = None,
        shift: str | None = None,
        offset: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        service: BatchService = Depends(get_batch_service),
):
    batches = await service.list_batches(
        is_closed=is_closed,
        batch_number=batch_number,
        batch_date=batch_date,
        work_center_id=work_center_id,
        shift=shift,
        offset=offset,
        limit=limit,
    )
    return batches


@router.post("/{batch_id}/aggregate", response_model=AggregateResult)
async def aggregate_products(
        batch_id: int,
        data: AggregateRequest,
        service: ProductService = Depends(get_product_service),
):
    result = await service.aggregate_products(batch_id, data.unique_codes)
    if result is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return result