
from typing import Final
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append('../')
from information_services_backend import config

Base: Final = declarative_base()


class AsyncDatabase:
    """
    Асинхронный базовый класс для подключения к базе данных.
    """
    def __init__(self, connection_string: str):
        self._engine = create_async_engine(connection_string, echo=False)
        self._session_factory = sessionmaker(self._engine, expire_on_commit=False, class_=AsyncSession)

    async def get_session(self) -> AsyncSession:
        async with self._session_factory() as session:
            yield session


class MysqlDatabaseTwo(AsyncDatabase):
    def __init__(self):
        super().__init__(config.connection_mysql_two)


class MysqlDatabaseThree(AsyncDatabase):
    def __init__(self):
        super().__init__(config.connection_mysql_three)

