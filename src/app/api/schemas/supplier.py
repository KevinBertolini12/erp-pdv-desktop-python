from pydantic import BaseModel, Field


class SupplierBase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    document: str | None = Field(default=None, max_length=30)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=120)


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    document: str | None = Field(default=None, max_length=30)
    phone: str | None = Field(default=None, max_length=30)
    email: str | None = Field(default=None, max_length=120)


class SupplierRead(SupplierBase):
    id: int
