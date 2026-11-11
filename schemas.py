from typing import Annotated, Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


TagValue = Annotated[str, Field(min_length=1, max_length=100)]


class AssetCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    name: str = Field(min_length=1, max_length=100)
    asset_type: str = Field(alias="type", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    tags: list[TagValue] = Field(default_factory=list)
    created_by: str = Field(default="system", alias="createdBy", min_length=1, max_length=100)
    updated_by: Optional[str] = Field(default=None, alias="updatedBy", min_length=1, max_length=100)

    @field_validator("updated_by", mode="before")
    @classmethod
    def reject_null_updated_by(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("updatedBy must be a non-empty string when provided")
        return value


class AssetUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    asset_type: Optional[str] = Field(default=None, alias="type", min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    updated_by: Optional[str] = Field(default=None, alias="updatedBy", min_length=1, max_length=100)

    @field_validator("name", "asset_type", "updated_by", mode="before")
    @classmethod
    def reject_null_strings(cls, value: Any) -> Any:
        if value is None:
            raise ValueError("This field cannot be null when provided")
        return value

    @model_validator(mode="after")
    def require_asset_field(self) -> "AssetUpdate":
        allowed_fields = {"name", "asset_type", "description"}
        if not allowed_fields.intersection(self.model_fields_set):
            raise ValueError("Provide at least one field to update")
        return self


class AssetTagsCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    tags: list[TagValue] = Field(min_length=1)
    updated_by: str = Field(default="system", alias="updatedBy", min_length=1, max_length=100)


class AssetListFilters(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    asset_type: Optional[str] = Field(default=None, alias="type", min_length=1, max_length=100)
    tag: Optional[str] = Field(default=None, min_length=1, max_length=100)
