from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase

from app.config import API_ROOT, Settings


class Base(DeclarativeBase):
    pass


def create_runtime_engine(settings: Settings) -> Engine:
    return create_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
        hide_parameters=True,
        connect_args={"connect_timeout": 2},
    )


def expected_migration_heads() -> frozenset[str]:
    config = Config(str(API_ROOT / "alembic.ini"))
    return frozenset(ScriptDirectory.from_config(config).get_heads())


def database_is_ready(engine: Engine, expected_heads: frozenset[str]) -> bool:
    try:
        with engine.connect() as connection:
            connection.execute(text("SET LOCAL statement_timeout = '2s'"))
            current_heads = MigrationContext.configure(connection).get_current_heads()
            return bool(expected_heads) and frozenset(current_heads) == expected_heads
    except SQLAlchemyError:
        return False
