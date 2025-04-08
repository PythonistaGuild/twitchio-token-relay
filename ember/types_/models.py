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

from typing import TypedDict


class UserRecordDT(TypedDict):
    id: int
    twitch_id: str
    name: str
    token: str | None


class FullUserRecordDT(TypedDict, total=False):
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
