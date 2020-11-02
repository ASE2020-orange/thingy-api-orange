Thingy Quizz API Endpoints
===

| Verb | Path                    | Description                                      |
|------|-------------------------|--------------------------------------------------|
| GET  | `/api/games/`             | Get a list of all the games                      |
| POST | `/api/games/`             | Create a new game                                |
| POST | `/api/games/{id}/join/` | Join a game with a specific ID                   |
| POST | `/login/`                 | User login                                       |
| GET  | `/user/{id}/stats`     | Get a player stats (how many games won, etc\.) |
| GET | `/api/games/{id}/question`| Get question + associated multiple choice answers |
| POST | `/api/games/{id}/question`| Answer to a question with given answer id |
