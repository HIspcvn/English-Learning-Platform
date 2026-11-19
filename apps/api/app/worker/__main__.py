import logging
from time import sleep

from sqlalchemy.exc import OperationalError

from app.config import Settings
from app.database import create_runtime_engine
from app.worker.mail import deliver_one

logger = logging.getLogger("app.worker")


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = Settings()
    if settings.auth_mail_key_bytes is None:
        raise SystemExit("AUTH_MAIL_KEY is required by the verification mail worker")

    engine = create_runtime_engine(settings)
    try:
        while True:
            try:
                if not deliver_one(engine, settings):
                    sleep(1)
            except OperationalError:
                logger.warning("Verification mail worker could not reach PostgreSQL")
                sleep(5)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
