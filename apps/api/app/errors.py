from collections.abc import Mapping
from http import HTTPStatus

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException


class Problem(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str
    code: str
    request_id: str


class ProblemException(HTTPException):
    def __init__(self, status: int, code: str, detail: str) -> None:
        super().__init__(status_code=status, detail=detail)
        self.code = code


def documented_problem(description: str) -> dict:
    return {
        "description": description,
        "content": {"application/problem+json": {"schema": Problem.model_json_schema()}},
    }


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
