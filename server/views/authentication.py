import secrets
import jwt

from aiohttp import web
from aiohttp_cors import CorsViewMixin

from oauth import github_auth_url, get_github


key = secrets.token_urlsafe(64)

profiles = {}


def get_profile_from_request(request):
    if "Authorization" not in request.headers:
        print("Authorization header missing")
        return None

    authorization = request.headers["Authorization"]
    encoded_jwt = authorization[7:]
    try:
        decoded_jwt = jwt.decode(encoded_jwt, key, algorithms='HS256')
    except jwt.exceptions.DecodeError:
        print("Can't decode")
        return None

    if decoded_jwt["id"] not in profiles:
        print("Invalid profile")
        return None

    user = profiles[decoded_jwt["id"]]
    return user


class ProfileView(web.View, CorsViewMixin):
    async def get(self):
        user = get_profile_from_request(self.request)
        if user is None:
            return web.Response(status=401)

        profile = {
            "id": user.id,
            "avatar_url": user.avatar_url,
            "name": user.name,
        }

        return web.json_response({"profile": profile})


class OAuthView(web.View, CorsViewMixin):
    async def get(self):
        return web.json_response({"urls": {"github": github_auth_url}})

    async def post(self):
        content = await self.request.json()
        code = content["code"]

        g = await get_github(code)
        if g is None:
            return web.json_response({"error": "login error"})

        user = g.get_user()

        encoded_jwt = jwt.encode(
            {"id": user.id}, key, algorithm="HS256").decode("utf-8")
        profiles[user.id] = user

        return web.json_response({"jwt": encoded_jwt})

    async def delete(self):
        user = get_profile_from_request(self.request)
        if user is None:
            return web.Response(status=401)
        print("delete", user)
        del profiles[user.id]
        return web.json_response({})
