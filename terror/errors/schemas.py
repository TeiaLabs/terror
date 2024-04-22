import operator
import traceback
from datetime import datetime
from functools import partial
from typing import Callable, Optional, Type, Any

from boltons import iterutils
from bson import ObjectId
from pydantic import BaseModel, Field
from toolz import keyfilter


class StarletteRequest(BaseModel):
    headers: dict[str, str]
    method: str
    path: str
    path_params: Optional[dict[str, str]]
    query_string: str
    query_params: Optional[dict[str, str]]

    @classmethod
    def from_starlette(cls, request):
        req = dict(request)
        req_attrs = [
            "headers",
            "method",
            "path",
            "path_params",
            "query_string",
            "query_params",
        ]
        req = keyfilter(partial(operator.contains, req_attrs), req)

        def stringify_binaries(path, key, value):
            if isinstance(value, bytes):
                value = value.decode(encoding="latin-1")
            return key, value

        remapped = iterutils.remap(req, visit=stringify_binaries)
        remapped["headers"] = dict(remapped["headers"])
        return remapped


class ErrorResponse(BaseModel):
    msg: str
    type: str
    details: list[str]


class Error(BaseModel):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    request: StarletteRequest
    response: ErrorResponse

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str,
        }