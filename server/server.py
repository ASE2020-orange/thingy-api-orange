"""
ThingyQuizz API
Orange team : Goloviatinski Sergiy, Herbelin Ludovic, Margueron Raphaël, Vorpe Fabien
Advanced Software Engineering Course, MCS 2020

server.py
--------------------------------------------------------------------------
REST API for the game
"""
import json
import os
import random

from aiohttp import web, ClientSession, WSMsgType

import aiohttp_cors

from dotenv import load_dotenv
from views.authentication import ProfileView, OAuthView


API_PREFIX = '/api'

load_dotenv()

ws_clients = []

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


questions = []
i = 0
game_id = -1


async def home_page(request):
    return web.Response(
        text="<p>Hello the</p>",
        content_type="text/html")


async def game_exists(request):
    if game_id == -1:
        return web.json_response({"game_id": game_id})
    else:
        return web.json_response({"game_id": game_id})


async def create_game(request):
    req_json = await request.json()
    tdb_request = 'https://opentdb.com/api.php?amount=10&type=multiple'
    global game_id
    game_id = random.randint(1, 42)
    async with ClientSession() as session:
        # todo : escape stuff
        if 'category' in req_json:
            tdb_request = f"{tdb_request}&category={req_json['category']}"
        if 'difficulty' in req_json:
            tdb_request = f"{tdb_request}&difficulty={req_json['difficulty']}"

        async with session.get(tdb_request) as resp:
            global i
            global questions
            questions = []
            i = 0
            if resp.status == 200:
                json_response = json.loads(await resp.text())
                for result in json_response["results"]:
                    questions.append(result)
                for client in ws_clients:
                    await client.send_str("TO_CLIENT.GAME_STARTED")
                return web.json_response({"game_id": game_id})
            else:
                return web.json_response({"error": "OpenTriviaDB error"}, status=resp.status)


async def get_categories(request):
    async with ClientSession() as session:
        async with session.get('https://opentdb.com/api_category.php') as resp:
            if resp.status == 200:
                json_response = json.loads(await resp.text())
                return web.json_response(json_response)
            else:
                return web.json_response({'error': 'OpenTriviaDB error'}, status=resp.status)


async def get_question(request):
    global i
    game_id = int(request.match_info["id"])
    answers = [questions[i]["correct_answer"]] + \
        questions[i]["incorrect_answers"][:-1]
    answer_ids = list(range(len(answers)))
    return web.json_response({
        "category": questions[i]["category"],
        "question": questions[i]["question"],
        "answers": [{"answer_id": answer_ids[i], "answer":answers[i]} for i in range(len(answers))]
    })


async def answer_question(request):
    game_id = int(request.match_info["id"])
    data = await request.json()
    if "answer_id" not in data.keys():
        return web.json_response({"error": "You need to specify an answer id"}, status=400)

    if data["answer_id"] == 0:
        global i
        global questions
        i += 1
        if i == len(questions):
            game_id = -1
            i = 0
            for client in ws_clients:
                await client.send_str("TO_CLIENT.GAME_FINISHED")
        else:
            for client in ws_clients:
                await client.send_str("TO_CLIENT.NEXT_QUESTION")
        return web.json_response({"correct": True})
    else:
        return web.json_response({"correct": False})


async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            print(msg.data)
            if msg.data == "close":
                ws_clients.remove(ws)
                await ws.close()
            elif msg.data.startswith("TO_CLIENT"):
                for client in ws_clients:
                    await client.send_str(msg.data)
            elif msg.data == "CLIENT_CONNECT":
                ws_clients.append(ws)
        elif msg.type == WSMsgType.ERROR:
            ws_clients.remove(ws)
            print("ws connection closed with exception %s" %
                  ws.exception())

    print("websocket connection closed")

    return ws


app.add_routes([web.get("/ws", websocket_handler)])

cors.add(app.router.add_get("/", home_page, name="home"))

cors.add(app.router.add_route("*", "/profile/", ProfileView, name="profile"))
cors.add(app.router.add_route("*", "/oauth/", OAuthView, name="oauth"))

# game-related routes
cors.add(app.router.add_post(
    f"{API_PREFIX}/games/", create_game, name='create_game'))

cors.add(app.router.add_get(
    f"{API_PREFIX}/games/", game_exists, name='game_exists'))

"""
cors.add(app.router.add_get(f"{API_PREFIX}/games/", get_games, name='all_games'))
cors.add(app.router.add_post(f"{API_PREFIX}/games/{id}/join/", join_game, name='join_game'))
"""

cors.add(app.router.add_get(
    f"{API_PREFIX}/categories/", get_categories, name='get_categories'))

cors.add(app.router.add_get(
    API_PREFIX+'/games/{id:\d+}/question/', get_question, name='get_question'))
cors.add(app.router.add_post(
    API_PREFIX+'/games/{id:\d+}/question/', answer_question, name='answer_question'))
# user-related routes
"""
cors.add(app.router.add_post(f"/login/", user_login, name="user_login"))
cors.add(app.router.add_get(f"/user/{id}/stats/", get_stats, name="get_stats"))
"""

if __name__ == "__main__":
    SERVER_PORT = int(os.getenv("SERVER_PORT"))
    web.run_app(app, port=SERVER_PORT)
