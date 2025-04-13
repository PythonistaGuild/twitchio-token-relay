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
import secrets
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

    async def create_user(self, twitch_id: str, twitch_name: str) -> UserRecord:
        query = """
        INSERT INTO users (twitch_id, token, name) VALUES($1, $2, $3)
        ON CONFLICT (twitch_id) DO UPDATE SET name = $3
        RETURNING *
        """

        token = secrets.token_urlsafe(64)

        async with self.pool.acquire() as connection:
            row: UserRecord | None = await connection.fetchrow(query, twitch_id, token, twitch_name, record_class=UserRecord)

        assert row
        return row

    async def create_app(self, user_id: int, *, name: str, client_id: str) -> ApplicationRecord:
        query = """
        INSERT INTO applications(id, user_id, client_id, name, url, scopes, bot_scopes) VALUES($1, $2, $3, $4, $5, $6, $7)
        RETURNING *
        """

        id_ = secrets.token_hex(32)
        url = secrets.token_hex(10)
        scopes = ""
        bot_scopes = ""

        async with self.pool.acquire() as connection:
            row: ApplicationRecord | None = await connection.fetchrow(
                query,
                id_,
                user_id,
                client_id,
                name,
                url,
                scopes,
                bot_scopes,
                record_class=ApplicationRecord,
            )

        assert row
        return row

    async def delete_app(self, id_: str) -> None:
        query = """
        DELETE FROM applications WHERE id = $1
        """

        async with self.pool.acquire() as connection:
            await connection.execute(query, id_)

    async def fetch_app_by_uri(self, uri: str) -> ApplicationRecord | None:
        query = """
        SELECT * FROM applications WHERE url = $1
        """

        async with self.pool.acquire() as connection:
            row: ApplicationRecord | None = await connection.fetchrow(query, uri, record_class=ApplicationRecord)

        return row

    async def fetch_user_by_token(self, token: str) -> list[FullUserRecord]:
        query = """
        SELECT
            u.*,
            a.id AS application_id,
            a.client_id,
            a.name AS application_name,
            a.scopes,
            a.bot_scopes,
            a.auths,
            a.url,
            w.allowed
        FROM
            users u
        LEFT JOIN
            applications a ON u.id = a.user_id
        LEFT JOIN
            whitelist w ON a.id = w.application_id
        WHERE
            u.token = $1
        ORDER BY
            a.id, w.allowed;
        """

        async with self.pool.acquire() as connection:
            rows: list[FullUserRecord] = await connection.fetch(query, token, record_class=FullUserRecord)

        return rows

    async def fetch_user_by_id(self, user_id: int) -> list[FullUserRecord]:
        query = """
        SELECT
            u.*,
            a.id AS application_id,
            a.client_id,
            a.name AS application_name,
            a.scopes,
            a.bot_scopes,
            a.auths,
            a.url,
            w.allowed
        FROM
            users u
        LEFT JOIN
            applications a ON u.id = a.user_id
        LEFT JOIN
            whitelist w ON a.id = w.application_id
        WHERE
            u.id = $1
        ORDER BY
            a.id, w.allowed;
        """

        async with self.pool.acquire() as connection:
            rows: list[FullUserRecord] = await connection.fetch(query, user_id, record_class=FullUserRecord)

        return rows

    async def fetch_user_by_twitch(self, twitch_id: str) -> list[FullUserRecord]:
        query = """
        SELECT
            u.*,
            a.id AS application_id,
            a.client_id,
            a.name AS application_name,
            a.scopes,
            a.bot_scopes,
            a.auths,
            a.url,
            w.allowed
        FROM
            users u
        LEFT JOIN
            applications a ON u.id = a.user_id
        LEFT JOIN
            whitelist w ON a.id = w.application_id
        WHERE
            u.twitch_id = $1
        ORDER BY
            a.id, w.allowed;
        """

        async with self.pool.acquire() as connection:
            rows: list[FullUserRecord] = await connection.fetch(query, twitch_id, record_class=FullUserRecord)

        return rows
