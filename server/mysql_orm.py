import tortoise
from tortoise import Tortoise, run_async
from models import *
import datetime
import os
from dotenv import load_dotenv

# Load the .env into the environement
load_dotenv()


class MysqlOrm:
    instance = None

    def __init__(self):
        if self.instance is not None:
            raise Exception(
                "This class is a singleton, use the get_instance method !")

    @staticmethod
    async def get_instance():
        if MysqlOrm.instance is None:
            MysqlOrm.instance = MysqlOrm()
            await MysqlOrm.create_instance()

        return MysqlOrm.instance

    @staticmethod
    async def create_instance():
        user = os.getenv("MYSQL_USER")
        pwd = os.getenv("MYSQL_PASSWORD")
        host = os.getenv("MYSQL_HOST")
        port = int(os.getenv("MYSQL_PORT"))
        db = os.getenv("MYSQL_DATABASE")

        await Tortoise.init(
            db_url=f'mysql://{user}:{pwd}@{host}:{port}/{db}',
            modules={'models': ['models']}
        )

        await Tortoise.generate_schemas()

    async def close(self):
        await Tortoise.close_connections()

    async def create_user(self, user_oauth_token):
        user = Users(user_oauth_token=user_oauth_token, score=0)
        await user.save()
        return user

    async def create_quiz(self, date, difficulty, quiz_type, quiz_category):
        quiz = Quizzes(date=date, difficulty=difficulty,
                       quiz_type=quiz_type, quiz_category=quiz_category)
        await quiz.save()
        return quiz

    async def create_answer(self, question, title, is_correct):
        answer = Answers(question=question, title=title, is_correct=is_correct)
        await answer.save()
        return answer

    async def create_question(self, title):
        question = Questions(title=title)
        await question.save()
        return question

    async def add_m2m_user_quiz(self, user, quiz):
        await user.quizzes.add(quiz)

    async def add_m2m_quiz_question(self, quiz, question):
        await quiz.questions.add(question)

    async def create_user_answers(self, user, quiz, answer, answer_delay):
        user_answer = UserAnswers(
            user=user, quiz=quiz, answer=answer, answer_delay=answer_delay)
        await user_answer.save()

    async def get_all_users(self):
        return await Users.all()

    async def get_all_quizzes(self):
        return await Quizzes.all()

    async def get_question_by_title(self, title):
        try:
            question = await Questions.filter(title=title).get()
            return question
        except tortoise.exceptions.DoesNotExist:
            return None

    async def get_all_questions(self):
        return await Questions.all()

    async def get_all_answers(self):
        return await Answers.all()

    async def get_user_by_id(self, id):
        return await Users.filter(id=id).get()

    async def get_user_by_oauth_id(self, id):
        try:
            return await Users.filter(user_oauth_token=id).get()
        except tortoise.exceptions.DoesNotExist:
            return None


    async def get_quiz_by_id(self, id):
        return await Quizzes.filter(id=id).get()

    async def get_question_by_id(self, id):
        return await Questions.filter(id=id).get()

    async def get_answer_by_id(self, id):
        return await Answers.filter(id=id).get()

    async def get_questions_of_quiz(self, quizz_id):
        quiz = await self.get_quiz_by_id(quizz_id)

        questions = await quiz.questions.all()

        return questions


    async def get_quizzes_of_user(self, user_id):
        user = await self.get_user_by_id(user_id)

        quizzes = await user.quizzes.all()

        return quizzes


    async def get_answers_of_user(self, user_id):
        user = await self.get_user_by_id(user_id)

        user_user_answers = await user.user_answers.all()

        answers = []
        for user_answer in user_user_answers:
            await user_answer.fetch_related('answer')
            answer = user_answer.answer
            answers.append(answer)

        return answers

    async def get_answers_of_question(self, question_id):
        question = await self.get_question_by_id(question_id)

        answers = await question.answers.all()

        return answers


    async def get_user_user_answers(self, user_id):
        user = await self.get_user_by_id(user_id)

        user_user_answers = await user.user_answers.all()

        return user_user_answers


    async def user_add_score(self, user_id, score):
        user = await self.get_user_by_id(user_id)

        user.score += score

        await user.save()

        return score
