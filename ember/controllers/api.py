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
from starlette_plus import View, route, Response, Request


class APIView(View):
    
    @route("/login", methods=["GET"], prefix=False)
    async def login(self, request: Request) -> Response:
        return Response(status_code=200, content="asfhjshjdfg")
        
    @route("/logout", methods=["GET"], prefix=False)
    async def logout(self) -> Response:
        ...
    
    @route("/login/redirect", prefix=False)
    async def login_callback(self) -> ...:
        ...