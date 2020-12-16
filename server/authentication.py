"""
ThingyQuizz API
Orange team : Goloviatinski Sergiy, Herbelin Ludovic, Margueron Raphaël, Vorpe Fabien
Advanced Software Engineering Course, MCS 2020

authentication.py
--------------------------------------------------------------------------
Helper module to handle the user's authentication using OAuth2 (Github)
"""

import secrets
import jwt

from aiohttp import web
from aiohttp_cors import CorsViewMixin

from oauth import github_auth_url, get_github

from mysql_orm import MysqlOrm
import os

key = secrets.token_urlsafe(64)

profiles = {}

"""
Helper to decode the profile from the data passed in the request
Needs to contan authorization and JWT
"""
def get_profile_from_request(request):
    if "Authorization" not in request.headers:
        print("Authorization header is missing")
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
            "name": user.login,
            "avatar_url": user.avatar_url,
            "location": user.location,
            "bio": user.bio,
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

        mysql_orm = await MysqlOrm.get_instance()
        user_db = await mysql_orm.get_user_by_oauth_id(user.id)

        if not user_db:
            user_db = await mysql_orm.create_user(user.id)

        return web.json_response({"jwt": encoded_jwt,"score":user_db.score})

    async def delete(self):
        user = get_profile_from_request(self.request)
        if user is None:
            return web.Response(status=401)
        print("delete from global var", user)
        del profiles[user.id]
        return web.json_response({})
