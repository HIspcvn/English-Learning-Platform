from alembic import context
from sqlalchemy import MetaData, create_engine
from sqlalchemy.pool import NullPool

from app.config import Settings

target_metadata = MetaData()
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
