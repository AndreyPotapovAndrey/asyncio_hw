import os

from sqlalchemy import Integer, String
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_USER = os.getenv("POSTGRES_USER", "swapi_user")
POSTGRES_DB = os.getenv("POSTGRES_DB", "swapi_db")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRS_PORT = os.getenv("POSTGRES_PORT", "5431")

PG_DSN = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRS_PORT}/{POSTGRES_DB}"


engine = create_async_engine(PG_DSN)
Session = async_sessionmaker(
    engine, expire_on_commit=False
)  # Если expire_on_commit=True, то сессия будет  истекать
# ("протухать") после коммита. И обязательно нужно будет создавать новую.


class Base(
    DeclarativeBase, AsyncAttrs
):  # Делает некоторые аттрибуты ORM-моделей (миксин) ассинхронными. К ним можно
    # будет обращаться с помощью await
    pass


class SwapiPeople(Base):
    __tablename__ = "swapi_people"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    birth_year: Mapped[str] = mapped_column(String)
    eye_color: Mapped[str] = mapped_column(String(20))
    films: Mapped[str] = mapped_column(String)
    gender: Mapped[str] = mapped_column(String(20))
    hair_color: Mapped[str] = mapped_column(String(20))
    height: Mapped[str] = mapped_column(Integer)
    homeworld: Mapped[str] = mapped_column(String)
    mass: Mapped[str] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(50))
    skin_color: Mapped[str] = mapped_column(String(20))
    species: Mapped[str] = mapped_column(String)
    starships: Mapped[str] = mapped_column(String)
    vehicles: Mapped[str] = mapped_column(String)


async def init_db():
    async with engine.begin() as conn:  # Из engine вырываем одно подключение.
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(
            Base.metadata.create_all
        )  # Создаём все таблицы, описанные выше.
