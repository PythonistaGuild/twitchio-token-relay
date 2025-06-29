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

import asyncio
import json
import logging
import secrets
from typing import TYPE_CHECKING

import litestar
from litestar.exceptions import HTTPException
from litestar.handlers import send_websocket_stream  # type: ignore
from litestar.response import Redirect, Response

from ..config import config


if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from litestar import Request
    from litestar.connection import WebSocket
    from litestar.datastructures import State
    from litestar.stores.valkey import ValkeyStore

    from ..database import Database


__all__ = ("OAuthController",)


LOGGER: logging.Logger = logging.getLogger(__name__)


class OAuthController(litestar.Controller):
    path = "/oauth"

    @litestar.get("/{uri:str}")
    async def user_oauth_endpoint(self, request: Request[str, str, State], state: State, uri: str) -> Response[str | None]:
        # TODO: HTML Responses...

        db: Database = state.db
        app = await db.fetch_app_by_uri(uri)

        if not app:
            return Response("Application not found or not valid", status_code=404)

        client: asyncio.Queue[str] | None = state.clients.get(app.id)
        if not client:
            return Response("Application can not be authenticated currently. No websocket found.", status_code=404)

        scopes: str | None = request.query_params.get("scopes", request.query_params.get("scope", None))
        if not scopes:
            return Response("Scopes is a required parameter which is missing", status_code=400)

        force: str = str(bool(request.query_params.get("force_verify", None))).lower()
        domain = config["server"]["domain"]
        redirect = f"{domain}/oauth/redirect/{app.url}"

        state_ = secrets.token_hex(32)
        states: ValkeyStore = state.states
        await states.set(state_, state_, expires_in=300)

        url = (
            "https://id.twitch.tv/oauth2/authorize"
            f"?client_id={app.client_id}"
            f"&scope={scopes}"
            f"&redirect_uri={redirect}"
            "&response_type=code"
            f"&force_verify={force}"
            f"&state={state_}"
        )

        return Redirect(url)

    @litestar.get("/redirect/{uri:str}")
    async def user_redicrect_endpoint(self, request: Request[str, str, State], state: State, uri: str) -> Response[str]:
        error = request.query_params.get("error")

        if error:
            description = request.query_params.get("error_description")
            return Response(f"Unable to Authenticate: {description}")

        state_ = request.query_params.get("state")
        if not state_:
            return Response("Error: Missing state parameter.", status_code=400)

        states: ValkeyStore = state.states
        state_value = await states.get(state_)

        if not state_value:
            return Response("Error: Incorrect state parameter provided or the request timed-out", status_code=400)

        state_value = state_value.decode()
        if state_value != state_:
            return Response("Error: state values do not match.", status_code=400)

        code = request.query_params.get("code")
        if not code:
            return Response("Error: Missing code parameter.", status_code=400)

        await states.delete(state_)

        db: Database = state.db
        app = await db.fetch_app_by_uri(uri)

        if not app:
            return Response("Error: This application no longer exists.")

        client: asyncio.Queue[dict[str, str]] | None = state.clients.get(app.id)
        if not client:
            return Response("Error: Application can not be authenticated currently. No websocket found.", status_code=404)

        domain = config["server"]["domain"]
        redirect = f"{domain}/oauth/redirect/{app.url}"

        data = {
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect,
        }

        await client.put(data)

        # TODO: Wait for websocket...
        return Redirect("/oauth/success")

    @litestar.get("/success", media_type=litestar.MediaType.HTML)
    async def success_endpoint(self, request: Request[str, str, State]) -> str:
        html = """<div>Success. You can now close this page.</div>"""
        return html

    async def handler(self, queue: asyncio.Queue[dict[str, str]]) -> AsyncGenerator[str]:
        while True:
            try:
                data = await queue.get()
            except asyncio.QueueShutDown:
                break

            json_ = json.dumps(data)
            yield json_

    @litestar.websocket("/connect")
    async def websocket_endpoint(self, socket: WebSocket[str, str, State], state: State) -> None:
        # Litestar won't allow a custom Websocket Denial Response:
        # https://github.com/litestar-org/litestar/issues/4111

        headers = socket.headers

        auth = headers.get("Authorization")
        app_id = headers.get("Application-ID")

        if not auth:
            raise HTTPException({"error": "Unauthorized. No Authorization header present."}, status_code=401)

        if not app_id:
            raise HTTPException({"error": "Missing 'Application-ID' header."}, status_code=400)

        db: Database = state.db
        user = await db.fetch_user_by_token(auth)

        if not user:
            raise HTTPException({"error": "Unauthorized. No user matches the provided token."}, status_code=401)

        first = user[0]
        if first.application_id != app_id:
            raise HTTPException({"error": "Incorrect Application-ID passed."}, status_code=400)

        if app_id in state.clients:
            raise HTTPException(
                {"error": "The Application-ID already has an associated websocket connected."}, status_code=409
            )

        queue: asyncio.Queue[dict[str, str]] = asyncio.Queue()
        state.clients[app_id] = queue

        try:
            await socket.accept()
            await send_websocket_stream(socket=socket, stream=self.handler(queue), listen_for_disconnect=True)
        except Exception:
            state.clients.pop(app_id, None)

        state.clients.pop(app_id, None)

    @litestar.get("/status")
    async def websocket_status_endpoint(self, request: Request[str, str, State], state: State) -> Redirect | dict[str, bool]:
        if not request.session:
            return Redirect("/")

        db: Database = state.db
        rows = await db.fetch_user_by_id(request.session["id"])

        if not rows:
            request.clear_session()
            return Redirect("/")

        first = rows[0]
        client = state.clients.get(first.application_id)

        data = {"status": bool(client)}
        return data
