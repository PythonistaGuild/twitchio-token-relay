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

import pathlib
from typing import TYPE_CHECKING, Any

from aiohttp import ClientSession
from litestar import Litestar, get
from litestar.logging import LoggingConfig
from litestar.middleware.session.server_side import ServerSideSessionConfig
from litestar.params import ParameterKwarg
from litestar.response.file import File
from litestar.router import Router
from litestar.static_files import create_static_files_router  # type: ignore
from litestar.stores.valkey import ValkeyStore

from .config import config
from .controllers import *
from .database import Database


if TYPE_CHECKING:
    from litestar import Controller
    from litestar.middleware import DefineMiddleware
    from litestar.stores.base import Store


@get("/")
async def dynamic_dist_route(name: str) -> File:
    dist = config["server"]["build"]
    return File(f"{dist}/{name}.html", media_type="text/html", content_disposition_type="inline")


class App(Litestar):
    def __init__(self, **kwargs: Any) -> None:
        self.config = config

        store = ValkeyStore.with_client(db=config["valkey"]["db"], port=config["valkey"]["port"])
        stores: dict[str, Store] = {"sessions": store}

        sessions = ServerSideSessionConfig(max_age=config["sessions"]["max_age"], renew_on_access=True, secure=True, httponly=False)
        middleware: list[DefineMiddleware] = [sessions.middleware]

        static = create_static_files_router(
            path="/assets",
            directories=["eira/dist/assets"],
        )
        handlers: list[type[Controller] | Router] = [APIControllerV1, SessionsController, static]

        logging_config = LoggingConfig(
            root={"level": "INFO", "handlers": ["queue_listener"]},
            formatters={"standard": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}},
            log_exceptions="always",
        )

        super().__init__(  # type: ignore
            route_handlers=handlers,
            stores=stores,
            middleware=middleware,
            on_startup=[self.on_startup],
            on_shutdown=[self.on_shutdown],
            logging_config=logging_config,
            **kwargs,
        )

    async def on_startup(self, app: Litestar) -> None:
        # Database...
        dsn = config["database"]["dsn"]

        db = Database(dsn=dsn)
        await db.connect()

        app.state.db = db

        # State store...
        store = ValkeyStore.with_client(db=config["valkey"]["db"], port=config["valkey"]["port"])
        app.state.states = store

        # aiohttp Session
        session = ClientSession()
        app.state.aiohttp = session

        # Add built routes from frontend
        dist = config["server"]["build"]
        root = pathlib.Path(dist)

        for path in root.glob("*.html"):
            name = path.name.removesuffix(".html")
            route_path = f"/{name}" if name != "index" else "/"

            route = Router(
                route_path,
                route_handlers=[dynamic_dist_route],
                parameters={"name": ParameterKwarg(default=name, const=True)},
            )
            self.register(route)

    async def on_shutdown(self, app: Litestar) -> None:
        db: Database | None = app.state.get("db")
        sess: ClientSession | None = app.state.get("aiohttp")

        if db:
            await db.close()

        if sess:
            await sess.close()
