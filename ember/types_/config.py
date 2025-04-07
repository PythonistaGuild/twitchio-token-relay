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


class ServerT(TypedDict):
    port: int
    host: str
    domain: str


class SessionsT(TypedDict):
    max_age: int


class ValkeyT(TypedDict):
    db: int
    port: int


class DatabaseT(TypedDict):
    dsn: str


class TwitchT(TypedDict):
    client_id: str
    client_secret: str


class ConfigT(TypedDict):
    server: ServerT
    sessions: SessionsT
    valkey: ValkeyT
    database: DatabaseT
    twitch: TwitchT
