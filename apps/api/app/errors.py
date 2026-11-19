from collections.abc import Mapping
from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class Problem(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str
    request_id: str


def problem_response(
    request: Request,
    status: int,
    code: str,
    detail: str,
    *,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    problem = Problem(
        type="about:blank",
        title=HTTPStatus(status).phrase,
        status=status,
        detail=detail,
        instance=request.url.path,
        code=code,
        request_id=request.state.request_id,
    )
    return JSONResponse(
        problem.model_dump(),
        status_code=status,
        media_type="application/problem+json",
        headers={**(headers or {}), "Cache-Control": "no-store"},
    )
