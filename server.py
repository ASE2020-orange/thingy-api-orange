"""
ThingyQuizz API
Orange team : Goloviatinski Sergiy, Herbelin Ludovic, Margueron Raphaël, Vorpe Fabien
Advanced Software Engineering Course, MCS 2020

server.py
--------------------------------------------------------------------------
REST API for the game
"""

from aiohttp import web
import aiohttp_cors

API_PREFIX = '/api'

app = web.Application()

# Configure default CORS settings.
cors = aiohttp_cors.setup(app, defaults={
    "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
            allow_methods="*",
        )
})


# game-related routes
"""
cors.add(app.router.add_get(f"{API_PREFIX}/games/", get_games, name='all_games'))
cors.add(app.router.add_post(f"{API_PREFIX}/games/", create_game, name='create_game'))
cors.add(app.router.add_post(f"{API_PREFIX}/games/{id}/join/", join_game, name='join_game'))
"""

# user-related routes
"""
cors.add(app.router.add_post(f"{API_PREFIX}/login/", user_login, name='user_login'))
cors.add(app.router.add_get(f"{API_PREFIX}/user/{id}/stats/", get_stats, name='get_stats'))
"""


if __name__ == "__main__":
    web.run_app(app, port=8080)