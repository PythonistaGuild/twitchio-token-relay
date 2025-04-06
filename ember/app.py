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

from litestar import Litestar
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.stores.valkey import ValkeyStore

from .config import config
from .controllers import *


if TYPE_CHECKING:
    from litestar import Controller
    from litestar.middleware import DefineMiddleware


class App(Litestar):
    def __init__(self, **kwargs: Any) -> None:
        self.config = config

        store = ValkeyStore.with_client(db=config["valkey"]["db"], port=config["valkey"]["port"])
        stores: dict[str, ValkeyStore] = {"sessions": store}

        sessions = ServerSideSessionConfig(max_age=config["sessions"]["max_age"], renew_on_access=True, secure=True)
        middleware: list[DefineMiddleware] = [sessions.middleware]

        controllers: list[type[Controller]] = [APIControllerV1]
        super().__init__(route_handlers=controllers, stores=stores, middleware=middleware, **kwargs)  # type: ignore
