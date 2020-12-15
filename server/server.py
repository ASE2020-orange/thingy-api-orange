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
from datetime import datetime

from aiohttp import web, ClientSession, WSMsgType

import aiohttp_cors

from dotenv import load_dotenv
from views.authentication import ProfileView, OAuthView
from mysql_orm import MysqlOrm
from models import *
import asyncio


API_PREFIX = '/api'

load_dotenv()

ws_clients = []
ws_thingy = {}

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
previous_question_time = -1
user_id = -1
quiz = -1
answers = []


loop = asyncio.get_event_loop()
conn = loop.run_until_complete(MysqlOrm.get_instance('root', 'mysql', 'localhost', 3306, 'test'))


async def home_page(request):
    return web.Response(
        text="<p>Hello there</p>",
        content_type="text/html")


async def game_exists(request):
    global game_id
    return web.json_response({"game_id": game_id})


async def create_game(request):
    global game_id
    global quiz

    req_json = await request.json()
    tdb_request = 'https://opentdb.com/api.php?amount=10&type=multiple'
    
    game_id = random.randint(1, 42)
    async with ClientSession() as session:
        # todo : escape stuff
        difficulty = 'Medium'
        category = 0

        if 'category' in req_json:
            category = int(req_json['category'])
            tdb_request = f"{tdb_request}&category={req_json['category']}"
        if 'difficulty' in req_json:
            difficulty = req_json['difficulty']

        tdb_request = f"{tdb_request}&category={category}&difficulty={difficulty}"
        quiz = await conn.create_quiz(date=datetime.now(), difficulty=difficulty, quiz_type='multiple', quiz_category=category)

        async with session.get(tdb_request) as resp:
            global i
            global questions
            global answers
            questions = []
            i = 0
            if resp.status == 200:
                json_response = json.loads(await resp.text())
                for result in json_response["results"]:
                    questions.append(result)
                    question = await conn.create_question(result['question'])

                    question_answers = []

                    await conn.create_quiz_question(quiz, question)

                    for answer_title in result['incorrect_answers']:
                        answer = await conn.create_answer(question, answer_title, is_correct=False)
                        question_answers.append(answer)

                    answer = await conn.create_answer(question, result['correct_answer'], is_correct=True)
                    question_answers.append(answer)
                    answers.append(question_answers)

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
    global previous_question_time

    if previous_question_time != -1:
        current_question_time = datetime.now()
        elapsed = current_question_time - previous_question_time
        previous_question_time = current_question_time

        if elapsed.seconds >= 10:
            i += 1
    else:
        previous_question_time = datetime.now()
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
    # todo : add user_id to request or something
    global i
    global user_id

    game_id = int(request.match_info["id"])
    data = await request.json()
    if "answer_id" not in data.keys():
        return web.json_response({"error": "You need to specify an answer id"}, status=400)

    print(data)
    if data["thingy_id"] not in ws_thingy:
        return web.json_response({"error": "You need to specify a correct thingy ID"}, status=400)

    ws = ws_thingy[data["thingy_id"]]

    if(user_id != -1):
        user = await mysql_orm.get_user_by_id(user_id)
        answer_delay = (datetime.now() - previous_question_time).timestamp()
        answer = answers[i][data['answer_id']]
        await conn.create_user_answers(user, quiz, answer, answer_delay)


    if data["answer_id"] == 0:
        await ws.send_str("CORRECT")

        global questions

        i += 1
        if i == len(questions):
            game_id = -1
            i = 0
            for client in ws_clients:
                # todo send defeat to the thingy of people that didn't win
                await ws.send_str("VICTORY")
                # await ws.send_str("DEFEAT")
                await client.send_str("TO_CLIENT.GAME_FINISHED")
        else:
            for client in ws_clients:
                await client.send_str("TO_CLIENT.NEXT_QUESTION")
        return web.json_response({"correct": True})
    else:
        await ws.send_str("INCORRECT")
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
            elif msg.data.split(".")[0] == "THINGY_CONNECT":
                ws_thingy[int(msg.data[-1])] = ws
        elif msg.type == WSMsgType.ERROR:
            if ws in ws_clients:
                ws_clients.remove(ws)
            if ws in ws_thingy:
                ws_thingy.remove(ws)
            print("ws connection closed with exception %s" %
                  ws.exception())

    print("websocket connection closed")

    return ws


app.add_routes([web.get("/ws", websocket_handler)])


async def create_user(request):
    data = await request.json()

    mysql_orm = await MysqlOrm.get_instance()

    user = await mysql_orm.create_user(data['user_oauth_token'])

    global user_id
    user_id = user.id

    return web.json_response(vars(user))


async def get_user(request):
    id = int(request.match_info['id'])
    print(id)

    mysql_orm = await MysqlOrm.get_instance()

    user = await mysql_orm.get_user_by_id(id)

    global user_id
    user_id = id

    if len(user) == 0:
        return web.json_response({'id': -1})
    else:
        user = user[0]
        return web.json_response(vars(user))


async def get_user_answer(request):
    user_id = int(request.match_info['id'])

    mysql_orm = await MysqlOrm.get_instance()

    user_answers = await mysql_orm.get_answers_of_user(user_id)

    return web.json_response({"nb_answers": len(user_answers), "answers": [vars(user_answer) for user_answer in user_answers]})





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

# DB related routes
cors.add(app.router.add_post('/users/', create_user, name='create_user'))
cors.add(app.router.add_get('/users/{id:\d+}/', get_user, name='get_user'))
cors.add(app.router.add_get('/answers/users/{id:\d+}', get_user_answer, name='get_user_answer'))


# user-related routes
"""
cors.add(app.router.add_post(f"/login/", user_login, name="user_login"))
cors.add(app.router.add_get(f"/user/{id}/stats/", get_stats, name="get_stats"))
"""

if __name__ == "__main__":
    try:
        SERVER_PORT = int(os.getenv("SERVER_PORT"))
    except ValueError:
        SERVER_PORT = 1080
    web.run_app(app, port=SERVER_PORT, host="0.0.0.0")
