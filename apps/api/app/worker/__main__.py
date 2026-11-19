import logging
from time import monotonic, sleep

from sqlalchemy.exc import OperationalError

from app.config import Settings
from app.database import create_runtime_engine
from app.identity.sessions import retire_expired_sessions
from app.worker.mail import deliver_one

logger = logging.getLogger("app.worker")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    if settings.auth_mail_key_bytes is None:
        raise SystemExit("AUTH_MAIL_KEY is required by the verification mail worker")

    engine = create_runtime_engine(settings)
    next_session_cleanup = monotonic()
    try:
        while True:
            try:
                if monotonic() >= next_session_cleanup:
                    retire_expired_sessions(engine)
                    next_session_cleanup = monotonic() + 60
                if not deliver_one(engine, settings):
                    sleep(1)
            except OperationalError:
                logger.warning("Identity worker could not reach PostgreSQL")
                sleep(5)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
