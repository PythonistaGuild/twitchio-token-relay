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

import logging
import secrets
from typing import TYPE_CHECKING, Any

import asyncpg
import litestar
from litestar.response import Redirect, Response

from ..config import config
from ..types_.models import UserRecordDT  # noqa: TC001 [Litestar uses this at runtime]


if TYPE_CHECKING:
    import asyncio

    from aiohttp import ClientSession
    from litestar import Request
    from litestar.datastructures import State
    from litestar.stores.valkey import ValkeyStore

    from ..database import Database


__all__ = ("SessionsController",)


LOGGER: logging.Logger = logging.getLogger(__name__)

TWITCH_OAUTH_URL = "https://id.twitch.tv/oauth2/authorize"
TWITCH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"
TWITCH_VALIDATE_URL = "https://id.twitch.tv/oauth2/validate"


class SessionsController(litestar.Controller):
    path = "/users"

    @property
    def headers(self) -> dict[str, str]:
        return {"Content-Type": "application/x-www-form-urlencoded"}

    @litestar.get("/login")
    async def login_endpoint(self, request: Request[str, str, State], state: State) -> Redirect:
        if request.session:
            return Redirect("/")

        client_id = config["twitch"]["client_id"]
        redirect_uri = f"{config['server']['domain']}/users/redirect"
        scopes = "user%3Aread%3Aemail"

        state_ = secrets.token_hex(32)
        states: ValkeyStore = state.states
        await states.set(state_, state_, expires_in=300)

        url = (
            f"{TWITCH_OAUTH_URL}"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            "&response_type=code"
            f"&scope={scopes}"
            f"&state={state_}"
        )

        return Redirect(url)

    @litestar.get("/logout")
    async def logout_endpoint(self, request: Request[str, str, State]) -> Redirect:
        if request.session:
            request.clear_session()

        return Redirect("/")

    @litestar.get("/redirect")
    async def redirect_endpoint(self, request: Request[str, str, State], state: State) -> Redirect | Response[str]:
        if request.session:
            return Redirect("/")

        error = request.query_params.get("error")

        if error:
            description = request.query_params.get("error_description")
            LOGGER.warning("OAuth Login failed: %s", description)

            return Redirect("/")

        state_ = request.query_params.get("state")
        if not state_:
            return Response("Error: Missing state parameter. Try logging in again...", status_code=400)

        states: ValkeyStore = state.states
        state_value = await states.get(state_)

        if not state_value:
            return Response(
                "Error: Incorrect state parameter provided or the request timed-out. Try logging in again.", status_code=400
            )

        state_value = state_value.decode()
        if state_value != state_:
            return Response("Error: state values do not match. Try logging in again...", status_code=400)

        code = request.query_params.get("code")
        if not code:
            return Response("Error: Missing code parameter.", status_code=400)

        await states.delete(state_)

        data = {
            "client_id": config["twitch"]["client_id"],
            "client_secret": config["twitch"]["client_secret"],
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": f"{config['server']['domain']}/users/redirect",
        }

        sess: ClientSession = state.aiohttp

        async with sess.post(TWITCH_TOKEN_URL, data=data, headers=self.headers) as resp:
            if resp.status > 200:
                return Response("An internal error occurred. Try again.", status_code=500)

            data = await resp.json()
            token: str = data["access_token"]

        validate_headers = {"Authorization": f"OAuth {token}"}
        async with sess.get(TWITCH_VALIDATE_URL, headers=validate_headers) as resp:
            if resp.status > 200:
                return Response("An internal error occurred. Try again.", status_code=500)

            data = await resp.json()
            user_id: str = data["user_id"]
            user_login: str = data["login"]

        if not user_id:
            Response("An internal error occurred. Try again.", status_code=500)

        db: Database = state.db
        data = await db.create_user(user_id, user_login)

        request.set_session(data.to_dict(include_token=False))  # type: ignore
        return Redirect("/")

    @litestar.get("/@me")
    async def current_user_endpoint(self, request: Request[str, str, State], state: State) -> dict[str, Any] | None:
        if not request.session:
            return None

        db: Database = state.db
        rows = await db.fetch_user_by_id(request.session["id"])

        if not rows:
            request.clear_session()
            return None

        first = rows[0]
        client = state.clients.get(first.client_id)

        data = {
            "id": first.id,
            "twitch_id": first.twitch_id,
            "name": first.name,
            "applications": [app.to_dict() for app in rows if app.application_id is not None],
            "status": bool(client),
        }

        return data

    @litestar.post("/apps")
    async def create_app_endpoint(
        self,
        request: Request[str, str, State],
        state: State,
        data: dict[str, str],
    ) -> Response[str] | dict[str, Any]:
        if not request.session:
            return Response("Unauthorized", status_code=401)

        if not data:
            return Response("Missing application data", status_code=400)

        client_id = data.get("client_id")
        name = data.get("name")

        if not client_id or not name:
            fields = ", ".join(["name" if not name else "", "client_id" if not client_id else ""])
            return Response(f"Missing the following application fields: {fields}")

        db: Database = state.db
        rows = await db.fetch_user_by_id(request.session["id"])

        if not rows:
            request.clear_session()
            return Response("Unauthorized", status_code=401)

        first = rows[0]
        if first.application_id is not None:
            return Response("You currently have too many applications.", status_code=409)

        try:
            new_row = await db.create_app(first.id, name=name, client_id=client_id)
        except asyncpg.UniqueViolationError:
            return Response("An application with the provided Client-ID already exists.", status_code=403)

        resp = {
            "id": first.id,
            "twitch_id": first.twitch_id,
            "name": first.name,
            "applications": [new_row.to_dict()],
        }
        return resp

    @litestar.delete("/apps", status_code=200)
    async def delete_app_endpoint(
        self,
        request: Request[str, str, State],
        state: State,
        data: dict[str, str],
    ) -> None | Response[str]:
        if not request.session:
            return Response("Unauthorized", status_code=401)

        if not data:
            return Response("Missing application data", status_code=400)

        application_id = data.get("application_id")

        if not application_id:
            return Response("Missing 'application_id' field", status_code=400)

        db: Database = state.db
        rows = await db.fetch_user_by_id(request.session["id"])

        if not rows:
            request.clear_session()
            return Response("Unauthorized", status_code=401)

        first = rows[0]
        if first.application_id != application_id:
            return Response("Incorrect 'application_id' passed. No matching application", status_code=400)

        try:
            await db.delete_app(application_id)
        except Exception as e:
            return Response(f"Unexpected error occurred. Try again later: {e}", status_code=500)

        queue: asyncio.Queue[Any] | None = state.clients.get(first.client_id, None)
        if queue:
            queue.shutdown(immediate=True)

    @litestar.get("/token")
    async def new_token_endpoint(self, request: Request[str, str, State], state: State) -> Redirect | UserRecordDT:
        if not request.session:
            return Redirect("/")

        db: Database = state.db
        rows = await db.fetch_user_by_id(request.session["id"])

        if not rows:
            request.clear_session()
            return Redirect("/")

        user = rows[0]
        new = await db.update_token(user.id)

        return new.to_dict()
