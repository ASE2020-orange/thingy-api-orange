"""
ThingyQuizz API
Orange team : Goloviatinski Sergiy, Herbelin Ludovic, Margueron Raphaël, Vorpe Fabien
Advanced Software Engineering Course, MCS 2020

server.py
--------------------------------------------------------------------------
REST API for the game
"""

from aiohttp import web, ClientSession, WSMsgType
import aiohttp_cors
import sys
import json
import random

ws_clients = []

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


questions = []
i = 0


async def home_page(request):
    return web.Response(
        text='<p>Hello there!</p>',
        content_type='text/html')


async def create_game(request):
    game_id = random.randint(1, 42)
    async with ClientSession() as session:
        async with session.get('https://opentdb.com/api.php?amount=10&type=multiple') as resp:
            if resp.status == 200:
                json_response = json.loads(await resp.text())
                for result in json_response['results']:
                    questions.append(result)

                return web.json_response({'game_id': game_id})
            else:
                return web.json_response({'error': 'OpenTriviaDB error'}, status=resp.status)


async def get_question(request):
    game_id = int(request.match_info['id'])
    answers = [questions[i]['correct_answer']] + \
        questions[i]['incorrect_answers'][:-1]
    answer_ids = list(range(len(answers)))
    return web.json_response({
        'category': questions[i]['category'],
        'question': questions[i]['question'],
        'answers': [{'answer_id': answer_ids[i], 'answer':answers[i]} for i in range(len(answers))]
    })


async def answer_question(request):
    game_id = int(request.match_info['id'])
    data = await request.json()
    if 'answer_id' not in data.keys():
        return web.json_response({'error': 'You need to specify an answer id'}, status=400)

    if data['answer_id'] == 0:
        global i
        i += 1
        i %= 10
        return web.json_response({'correct': True})
    else:
        return web.json_response({'correct': False})


async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            elif msg.data.startswith("TO_CLIENT"):
                for client in ws_clients:
                    await client.send_str(msg.data)
            else:
                ws_clients.append(ws)

            print(msg.data)
        elif msg.type == WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    print('websocket connection closed')

    return ws


app.add_routes([web.get('/ws', websocket_handler)])

cors.add(app.router.add_get(f"", home_page, name='home'))

# game-related routes
cors.add(app.router.add_get(
    f"{API_PREFIX}/games/", create_game, name='create_game'))
"""
cors.add(app.router.add_get(f"{API_PREFIX}/games/", get_games, name='all_games'))
cors.add(app.router.add_post(f"{API_PREFIX}/games/{id}/join/", join_game, name='join_game'))
"""
cors.add(app.router.add_get(
    API_PREFIX+'/games/{id:\d+}/question/', get_question, name='get_question'))
cors.add(app.router.add_post(
    API_PREFIX+'/games/{id:\d+}/question/', answer_question, name='answer_question'))
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
        port = 8080

    web.run_app(app, port=port)
