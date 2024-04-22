import operator
import traceback
from datetime import UTC, datetime
from functools import partial
from typing import Callable, Type

from boltons import iterutils
from bson import ObjectId
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from starlette.background import BackgroundTask
from starlette.requests import Request
from toolz import keyfilter

from .settings import Settings


def add_exception_handlers(app: FastAPI) -> None:
    exception_handlers = [
        (500, ValueError),
        (500, PyMongoError),
        (500, Exception),
    ]
    for status_code, exc_type in exception_handlers:
        handler = handler_factory(status_code, exc_type)
        app.add_exception_handler(exc_type, handler)


def handler_factory(
    status_code: int, exc_type: Type[Exception]
) -> Callable[[Request, Exception], JSONResponse]:
    def handler(req, exc):
        if not hasattr(exc, "details"):
            exc.details = "".join(traceback.format_exception(exc))
        if not hasattr(exc, "msg"):
            exc.msg = "An unknown error occurred."
        error_id = ObjectId()
        error_obj = dict(
            details=str(exc.details).split("\n"),
            error_id=str(error_id),
            msg=exc.msg,
            type=f"{exc_type.__name__}.{type(exc).__name__}",
        )
        task = BackgroundTask(_save_to_db, req, error_obj, error_id)
        return JSONResponse(
            status_code=status_code,
            content=error_obj,
            background=task,
        )

    return handler


def _save_to_db(request: Request, response: dict, error_id: ObjectId):
    sets = Settings()
    client = MongoClient(sets.TERROR_MONGODB_URI)
    collection = client[sets.TERROR_MONGODB_DBNAME]["errors"]
    req = _serialize_startlette_request(request)
    extra = {
        "_id": error_id,
        "created_at": datetime.now(UTC),
        "request": req,
        "response": response,
    }
    collection.insert_one(response | extra)
    client.close()


def _serialize_startlette_request(request: Request) -> dict:
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
