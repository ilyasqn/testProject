import uuid
from abc import ABC, abstractmethod

from fastapi.requests import Request
from loguru import logger

from src.db import async_session_maker
from src.repositories.message import MessageRepository

class IUnitOfWork(ABC):
    message: MessageRepository

    session_factory = None
    _session = None
    _session_id_prefix = 'notset'
    _session_id_body = str(uuid.uuid4())

    def init_repositories(self):
        self.message = MessageRepository(self.session)

    def set_session_id_prefix(self, value):
        self._session_id_prefix = value

    @property
    def session_id(self):
        return self._session_id_prefix + '-' + self._session_id_body

    @session_id.setter
    def session_id(self, value):
        self._session_id_prefix = value

    @property
    def session(self):
        if self._session is None:
            raise RuntimeError("An attempt to access the session was unsuccessful. Maybe you forgot to initialize it "
                               "via __aenter__ (async with uow)")
        return self._session

    @session.setter
    def session(self, value):
        self._session = value
        if value is not None:
            logger.debug("Session created and set")
        else:
            logger.debug("Session closed and set to None")
            self._session_id_prefix = 'session_none'

    @abstractmethod
    def __init__(self, request: Request):
        pass

    @abstractmethod
    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, *args):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass

    @abstractmethod
    async def get_session(self):
        pass


class UnitOfWork(IUnitOfWork):
    def __init__(self, info_dto: Request = None) -> None:
        self.logger = logger
        self.session_factory = async_session_maker

        if info_dto is not None:
            self._session_id_prefix = 'req'
            self._session_id_body = info_dto.state.session_id

        # session hierarchy
        # 0 - session is not initialized
        # n - session is initialized (n - nesting level)
        self._session_nesting_level = 0

    async def get_session(self):
        """ Возвращает сессию, если она уже существует, или создает новую сессию, если её нет. """
        if self._session is None:
            self._session = await self.session_factory()
            logger.debug(f"Session created: {self.session_id}")
        return self._session

    async def __aenter__(self):
        self._session_nesting_level += 1
        if self._session_nesting_level == 1:  # if session is not initialized
            self.session = self.session_factory()
            self.init_repositories()
            logger.debug(f"{self.session_id} [{self._session_nesting_level}] - ENTER - Session initialized")
        else:  # if session is initialized
            logger.debug(f"{self.session_id} [{self._session_nesting_level}] - ENTER")

    async def __aexit__(self, *args):
        if self._session_nesting_level == 1:
            if self._session is not None:
                await self.rollback()
            logger.debug(f"{self.session_id} [{self._session_nesting_level}] - EXIT - Session closed")
        else:
            logger.debug(f"{self.session_id} [{self._session_nesting_level}] - EXIT")
        self._session_nesting_level -= 1

    async def commit(self):
        if self._session_nesting_level == 1:
            await self.session.commit()
            await self.session.close()
            self.session = None
            logger.debug(f"{self.session_id} [{self._session_nesting_level}] - COMMIT")
        else:
            logger.debug(f"{self.session_id} [{self._session_nesting_level}] - COMMIT (ignored)")

    async def rollback(self):
        if self._session_nesting_level == 1:
            await self.session.rollback()
            await self.session.close()
            self.session = None
            logger.debug(f"{self.session_id} [{self._session_nesting_level}] - ROLLBACK")
        else:
            logger.debug(f"{self.session_id} [{self._session_nesting_level}] - ROLLBACK (ignored)")