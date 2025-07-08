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
import starlette_plus
import asyncio
import logging

import uvicorn

from app import App as App
from config import config as config


LOGGER: logging.Logger = logging.getLogger(__name__)


def create_app() -> App:
    app = App()
    return app


def main() -> None:
    starlette_plus.setup_logging(level=20, root=True)
    
    host = config["server"]["host"]
    port = config["server"]["port"]

    async def runner() -> None:
        conf = uvicorn.Config(
            "main:create_app",
            host=host,
            port=port,
            proxy_headers=True,
            forwarded_allow_ips="*",
            factory=True,
            access_log=False,
        )

        server = uvicorn.Server(conf)
        await server.serve()

    try:
        asyncio.run(runner())
    except KeyboardInterrupt:
        LOGGER.warning("Shutting down due to KeyboardInterrupt...")


if __name__ == "__main__":
    main()
