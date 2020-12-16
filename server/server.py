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
import tortoise

from aiohttp import web, ClientSession, WSMsgType

import aiohttp_cors

from dotenv import load_dotenv
from authentication import ProfileView, OAuthView, get_profile_from_request
from mysql_orm import MysqlOrm
from models import *
import asyncio

API_PREFIX = '/api'

SCORE_CORRECT = 5
SCORE_INCORRECT = -5

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


previous_question_time = -1
quiz = -1
question_count = 0


loop = asyncio.get_event_loop()
conn = loop.run_until_complete(MysqlOrm.get_instance())


async def home_page(request):
    text = """
    <p>
        Welcome to Thingy API, more informations on
        <a href='https://github.com/ASE2020-orange'>https://github.com/ASE2020-orange</a>
    </p>
    """
    return web.Response(
        text=text,
        content_type="text/html")


async def game_exists(request):
    global quiz
    if quiz == -1:
        return web.json_response({"game_id": -1})
    else:
        return web.json_response({"game_id": quiz.id})


difficulty_int_map = {'easy': 0, 'medium': 1, 'hard': 2}


async def create_game(request):
    global quiz
    global question_count

    req_json = await request.json()
    tdb_request = 'https://opentdb.com/api.php?amount=10&type=multiple'

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
        quiz = await conn.create_quiz(date=datetime.now(), difficulty=difficulty_int_map[difficulty], quiz_type='multiple', quiz_category=category)
        question_count = 0
        async with session.get(tdb_request) as resp:
            if resp.status == 200:
                json_response = json.loads(await resp.text())
                i = 0
                for result in json_response["results"]:
                    question = await conn.get_question_by_title(result['question'])
                    if not question:
                        question = await conn.create_question(result['question'])
                        for answer_title in result['incorrect_answers']:
                            await conn.create_answer(question, answer_title, is_correct=False)
                        await conn.create_answer(question, result['correct_answer'], is_correct=True)

                    await conn.add_m2m_quiz_question(quiz, question)

                for client in ws_clients:
                    await client.send_str("TO_CLIENT.GAME_STARTED")

                return web.json_response({"game_id": quiz.id})
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
    global previous_question_time
    global quiz
    global question_count

    if previous_question_time != -1:
        current_question_time = datetime.now()
        elapsed = current_question_time - previous_question_time
        previous_question_time = current_question_time

        if elapsed.seconds >= 10:
            question_count += 1
    else:
        previous_question_time = datetime.now()
    try:
        question = (await conn.get_questions_of_quiz(quiz.id))[question_count]
        question_count += 1

        incorrect_count = 0
        answers = []
        for answer in list(await conn.get_answers_of_question(question.id)):
            if answer.is_correct:
                answers.append(answer)
            else:
                incorrect_count += 1
                if incorrect_count < 3:
                    answers.append(answer)

        random.shuffle(answers)
        return web.json_response({
            "category": quiz.quiz_category,
            "question": question.title,
            "answers": [{"answer_id": answer.id, "answer": answer.title} for answer in answers]
        })
    # either question_count is too high for the number of question, or quiz = -1 because game is finished
    except (IndexError, AttributeError):
        for client in ws_clients:
            # await ws.send_str("DEFEAT")
            await client.send_str("TO_CLIENT.GAME_FINISHED")
            quiz = -1
            # no need to send response, the client will reset the GUI


async def answer_question(request):
    global quiz
    user = get_profile_from_request(request)

    if user:
        user_id = user.id
    else:
        user_id = -1

    data = await request.json()
    if "answer_id" not in data.keys():
        return web.json_response({"error": "You need to specify an answer id"}, status=400)

    if data["thingy_id"] not in ws_thingy:
        return web.json_response({"error": "You need to specify a correct thingy ID"}, status=400)

    ws = ws_thingy[data["thingy_id"]]
    answer = await conn.get_answer_by_id(data['answer_id'])
    if user_id != -1:
        user = await conn.get_user_by_oauth_id(user_id)
        answer_delay = (datetime.now() -
                        previous_question_time).total_seconds()
        await conn.create_user_answers(user, quiz, answer, answer_delay)

    if answer.is_correct:
        if user_id == -1:
            newscore = 0
        else:
            newscore = await conn.user_add_score(user.id, SCORE_CORRECT)
        await ws.send_str("CORRECT")

        global question_count

        question_count += 1
        try:
            (await conn.get_questions_of_quiz(quiz.id))[question_count]
            for client in ws_clients:
                await client.send_str("TO_CLIENT.NEXT_QUESTION")
        except IndexError:
            quiz = -1
            for client in ws_clients:
                # todo send defeat to the thingy of people that didn't win
                await ws.send_str("VICTORY")
                # await ws.send_str("DEFEAT")
                await client.send_str("TO_CLIENT.GAME_FINISHED")

        return web.json_response({"correct": True, "score": newscore})
    else:
        if user_id == -1:
            newscore = 0
        else:
            newscore = await conn.user_add_score(user.id, SCORE_INCORRECT)
        await ws.send_str("INCORRECT")
        return web.json_response({"correct": False, "score": newscore})


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


async def get_stats(request):
    oauth_id = int(request.match_info['oauth_id'])

    mysql_orm = await MysqlOrm.get_instance()

    user = await mysql_orm.get_user_by_oauth_id(oauth_id)

    quizzes = await mysql_orm.get_quizzes_of_user(user.id)
    nb_quizzes = len(quizzes)

    answers = await mysql_orm.get_answers_of_user(user.id)
    nb_answers = len(answers)
    nb_correct_answers = len([answer for answer in answers if answer.is_correct])
    nb_wrong_answers = len([answer for answer in answers if not answer.is_correct])
    percent_of_correct_answer = int(nb_correct_answers / nb_answers * 100)

    user_user_answers = await mysql_orm.get_user_user_answers(user.id)
    avg_reaction_time = sum([user_answer.answer_delay for user_answer in
                             user_user_answers]) / len(user_user_answers)

    return web.json_response(
        {"nb_quizzes": nb_quizzes, "nb_answers": nb_answers,
         "nb_correct_answers": nb_correct_answers,
         "nb_wrong_answers": nb_wrong_answers,
         "percent_of_correct_answer": percent_of_correct_answer,
         "avg_reaction_time": avg_reaction_time}
    )


app.add_routes([web.get("/ws", websocket_handler)])


cors.add(app.router.add_get("/", home_page, name="home"))

cors.add(app.router.add_route(
    "*", API_PREFIX+"/profile/", ProfileView, name="profile"))
cors.add(app.router.add_route(
    "*", API_PREFIX+"/oauth/", OAuthView, name="oauth"))

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
"""
cors.add(app.router.add_get(
    API_PREFIX+"/user/{oauth_id:\d+}/stats/", get_stats, name="get_stats"))


if __name__ == "__main__":

    try:
        SERVER_PORT = int(os.getenv("SERVER_PORT"))
    except ValueError:
        SERVER_PORT = 1080
    web.run_app(app, port=SERVER_PORT, host="0.0.0.0")
