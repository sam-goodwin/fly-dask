from pydantic import BaseModel
from typing import Any, Union


class FlyAppCreateRequest(BaseModel):
    app_name: str
    org_slug: Union[str, None] = None


class FlyAppCreateResponse(BaseModel):
    app_name: str
    org_slug: Union[str, None] = None


class FlyAppDetailsResponse(BaseModel):
    name: str
    status: str
    organization: dict[str, Any]


class FlyAppDeleteRequest(BaseModel):
    app_name: str
    org_slug: Union[str, None] = None


class FlyAppDeleteResponse(BaseModel):
    app_name: str
    status: int
