"""Copyright 2025 PythonistaGuild

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Self

import asyncpg

from .models import *


LOGGER: logging.Logger = logging.getLogger(__name__)


__all__ = ("Database",)


class Database:
    if TYPE_CHECKING:
        pool: asyncpg.Pool[asyncpg.Record]

    def __init__(self, *, dsn: str) -> None:
        self.dsn = dsn

    def __repr__(self) -> str:
        return f"Database(dsn={self.dsn})"

    async def connect(self) -> Self:
        if getattr(self, "pool", None):
            raise RuntimeError("Database has previously been connected.")

        self.pool = await asyncpg.create_pool(dsn=self.dsn)
        await self.setup()

        LOGGER.info("Successfully connected to %r.", self)
        return self

    async def setup(self) -> None:
        with open("SCHEMA.sql") as fp:
            await self.pool.execute(fp.read())

    async def close(self) -> None:
        try:
            async with asyncio.timeout(10):
                await self.pool.close()
        except TimeoutError:
            LOGGER.warning("Failed to gracefully close Database. Forcefully terminating.")
            self.pool.terminate()
        except Exception as e:
            LOGGER.error("Ignoring unknown exception in %r: %s", self, e)
        else:
            LOGGER.info("Successfully closed %r.", self)

    async def __aenter__(self) -> Self:
        return await self.connect()

    async def __aexit__(self, *args: Any, **kwargs: Any) -> None:
        await self.close()
