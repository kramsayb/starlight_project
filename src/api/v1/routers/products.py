from fastapi import APIRouter, Depends, HTTPException

from src.api.v1.schemas.batch import ProductRead
from src.api.v1.schemas.product import ProductCreate
from src.domain.exceptions import ProductAlreadyExistsError
from src.domain.services.product_service import ProductService
from src.core.dependencies import get_product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.post("", response_model=ProductRead, status_code=201)
async def create_product(
        data: ProductCreate,
        service: ProductService = Depends(get_product_service),
):
    fields = data.model_dump()
    try:
        result = await service.create_product(**fields)
    except ProductAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    if result is None:
        raise HTTPException(status_code=404, detail="Batch not found")
    return result