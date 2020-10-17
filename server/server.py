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
import sys

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

async def home_page(request):
    return web.Response(
        text='<p>Hello there!</p>',
        content_type='text/html')


cors.add(app.router.add_get(f"", home_page, name='home'))

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
    argv = sys.argv
    if(len(argv) >= 2):
        port = argv[1]
    else:
        port=8080
    
    web.run_app(app, port=1080)