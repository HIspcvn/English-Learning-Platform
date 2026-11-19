from alembic import context
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from app.config import Settings
from app.database import Base
from app.identity import models as _identity_models  # noqa: F401

target_metadata = Base.metadata
database_url = Settings().database_url.get_secret_value()

if context.is_offline_mode():
    context.configure(url=database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    engine = create_engine(database_url, poolclass=NullPool, hide_parameters=True)
    try:
        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)
            with context.begin_transaction():
                context.run_migrations()
    finally:
        engine.dispose()
