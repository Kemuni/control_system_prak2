from typing import Generator

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from config import settings


class Base(DeclarativeBase):
    """Базовый класс для всех SQLAlchemy моделей. Все другие модели должны наследоваться от него"""

    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

engine = create_engine(settings.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """Получаем сессию БД. Необходимо для инъекции зависимостей.    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

