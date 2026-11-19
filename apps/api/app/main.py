import json
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from time import perf_counter
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException

from app.config import Settings
from app.database import create_runtime_engine, database_is_ready, expected_migration_heads
from app.errors import Problem, problem_response
from app.identity.routes import router as identity_router

access_log = logging.getLogger("app.access")


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    if not access_log.hasHandlers():
        access_log.addHandler(logging.StreamHandler())
    access_log.setLevel(logging.INFO)

    application.state.migration_heads = expected_migration_heads()
    settings = Settings()
    application.state.settings = settings
    engine = create_runtime_engine(settings)
    application.state.engine = engine
    try:
        yield
    finally:
        engine.dispose()


app = FastAPI(
    title="English Learning Platform API",
    version="0.1.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url=None,
    lifespan=lifespan,
)
app.include_router(identity_router)


def request_id(header: str) -> str:
    if len(header) == 36:
        try:
            return str(UUID(header))
        except ValueError:
            pass
    return str(uuid4())


@app.middleware("http")
async def correlate_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    correlation_id = request_id(request.headers.get("X-Request-ID", ""))
    request.state.request_id = correlation_id
    started = perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = correlation_id
    if request.url.path.startswith("/health/"):
        response.headers["Cache-Control"] = "no-store"

    access_log.info(
        json.dumps(
            {
                "event": "request_completed",
                "request_id": correlation_id,
                "method": request.method,
                "status": response.status_code,
                "duration_ms": round((perf_counter() - started) * 1000, 2),
            }
        )
    )
    return response


@app.exception_handler(HTTPException)
async def handle_http_exception(request: Request, error: HTTPException) -> Response:
    return problem_response(
        request,
        error.status_code,
        "NOT_FOUND" if error.status_code == 404 else "HTTP_ERROR",
        "The requested operation could not be completed.",
        headers=error.headers,
    )


@app.exception_handler(RequestValidationError)
async def handle_validation_exception(request: Request, _error: RequestValidationError) -> Response:
    return problem_response(request, 422, "VALIDATION_ERROR", "The request was invalid.")


@app.exception_handler(OperationalError)
async def handle_database_outage(request: Request, _error: OperationalError) -> Response:
    return problem_response(
        request, 503, "SERVICE_NOT_READY", "The service is not ready.", headers={"Retry-After": "5"}
    )


class Liveness(BaseModel):
    status: Literal["ok"]


class Readiness(BaseModel):
    status: Literal["ready"]


@app.get("/health/live", operation_id="getLiveness")
def liveness() -> Liveness:
    return Liveness(status="ok")


@app.get(
    "/health/ready",
    operation_id="getReadiness",
    response_model=Readiness,
    responses={
        503: {
            "description": "The database or its migration state is unavailable.",
            "content": {"application/problem+json": {"schema": Problem.model_json_schema()}},
        }
    },
)
def readiness(request: Request) -> Readiness | Response:
    state = request.app.state
    if database_is_ready(state.engine, state.migration_heads):
        return Readiness(status="ready")
    return problem_response(request, 503, "SERVICE_NOT_READY", "The service is not ready.")
