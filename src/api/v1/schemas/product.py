from pydantic import BaseModel


class AggregateRequest(BaseModel):
    unique_codes: list[str]


class AggregationError(BaseModel):
    code: str
    reason: str


class AggregateResult(BaseModel):
    success: bool
    total: int
    aggregated: int
    failed: int
    errors: list[AggregationError]


class ProductCreate(BaseModel):
    unique_code: str
    batch_id: int