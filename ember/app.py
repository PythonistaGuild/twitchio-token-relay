"""Copyright (c) 2025 PythonistaGuild

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
from starlette_plus import Application, Redis, Request
from starlette_plus.middleware import RatelimitMiddleware, SessionMiddleware
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.responses import FileResponse
from controllers import *
from config import config

class App(Application):

    def __init__(self) -> None:
        redis = Redis(url=config["valkey"]["url"])
        ratelimiter = Middleware(RatelimitMiddleware, ignore_localhost=False, redis=redis)
        session = Middleware(SessionMiddleware, max_age=config["sessions"]["max_age"], secret=config["sessions"]["secret"], redis=redis,)
        super().__init__(access_log=True, views=[APIView(self)], middleware=[ratelimiter, session])

        self.mount("/static", app=StaticFiles(directory="eira/dist"), name="static")
        self.add_route("/dashboard", self.frontend_route)
        self.add_route("/dashboard/{path}", self.frontend_route)

    async def frontend_route(self, request: Request) -> FileResponse:
        return FileResponse("eira/dist/index.html", media_type="text/html", content_disposition_type="inline")