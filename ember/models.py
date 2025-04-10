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

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import asyncpg


if TYPE_CHECKING:
    from types_.models import ApplicationRecordDT, FullUserRecordDT, UserRecordDT


__all__ = ("ApplicationRecord", "FullUserRecord", "UserRecord")


class UserRecord(asyncpg.Record):
    id: int
    twitch_id: str
    name: str
    token: str

    def __getattr__(self, attr: str) -> Any:
        return self[attr]

    def to_dict(self, include_token: bool = True) -> UserRecordDT:
        return {
            "id": self.id,
            "twitch_id": self.twitch_id,
            "name": self.name,
            "token": self.token if include_token else None,
        }


class ApplicationRecord(asyncpg.Record):
    id: str
    user_id: int
    client_id: str
    name: str
    url: str
    scopes: str
    bot_scopes: str
    auths: int

    def __getattr__(self, attr: str) -> Any:
        return self[attr]

    def to_dict(self) -> ApplicationRecordDT:
        return {
            "application_id": self.id,
            "user_id": self.user_id,
            "client_id": self.client_id,
            "application_name": self.name,
            "url": self.url,
            "scopes": self.scopes,
            "bot_scopes": self.bot_scopes,
            "auths": self.auths,
        }


class FullUserRecord(asyncpg.Record):
    id: int
    twitch_id: str
    name: str
    token: str | None
    application_id: str | None
    client_id: str | None
    application_name: str | None
    scopes: str | None
    bot_scopes: str | None
    auths: int | None
    allowed: str | None

    def __getattr__(self, attr: str) -> Any:
        return self[attr]

    def to_dict(self, include_user: bool = False, include_token: bool = False) -> FullUserRecordDT:
        data: FullUserRecordDT = {}

        if include_user:
            data.update(
                {
                    "id": self.id,
                    "twitch_id": self.twitch_id,
                    "name": self.name,
                    "token": self.token if include_token else None,
                }
            )

        data.update(
            {
                "application_id": self.application_id,
                "client_id": self.client_id,
                "application_name": self.application_name,
                "scopes": self.scopes,
                "bot_scopes": self.bot_scopes,
                "auths": self.auths,
                "allowed": self.allowed,
            }
        )
        return data
