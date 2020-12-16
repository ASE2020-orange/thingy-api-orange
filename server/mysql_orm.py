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
            raise Exception("This class is a singleton, use the get_instance method !")

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
        user = Users(user_oauth_token=user_oauth_token)
        await user.save()
        return user


    async def create_quiz(self, date, difficulty, quiz_type, quiz_category):
        quiz = Quizzes(date=date, difficulty=difficulty, quiz_type=quiz_type, quiz_category=quiz_category)
        await quiz.save()
        return quiz


    async def create_answer(self, question, title, is_correct):
        answer = Answers(question=question, title=title, is_correct=is_correct)
        await answer.save()
        return answer

    async def create_quiz_question(self, quiz, question):
        quiz_question = QuizQuestions(quiz=quiz, question=question)
        await quiz_question.save()
        return quiz_question


    async def create_question(self, title):
        question = Questions(title=title)
        await question.save()
        return question


    async def add_m2m_user_quiz(self, user, quiz):
        await user.quizzes.add(quiz)


    async def add_m2m_user_answer(self, user, answer):
        await user.answers.add(quiz)


    async def add_m2m_quiz_question(self, quiz, question):
        await quiz.questions.add(question)


    async def create_user_answers(self, user, quiz, answer, answer_delay):
        user_answer = UserAnswers(user=user, quiz=quiz, answer=answer, answer_delay=answer_delay)
        await user_answer.save()


    async def get_all_users(self):
        return await Users.all()


    async def get_all_quizzes(self):
        return await Quizzes.all()

    async def get_question_by_title(self,title):
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


    async def get_answers_of_user(self, user_id):
        # answers = []

        user = await self.get_user_by_id(user_id)

        answers = await user.answers.all()

        return answers


    async def get_answers_of_question(self, question_id):
        question = await self.get_question_by_id(question_id)

        answers = await question.answers.all()

        return answers


async def test():
    mysql_orm = await MysqlOrm.get_instance()

    user = await mysql_orm.create_user(user_oauth_token="test_auth")
    user = await mysql_orm.get_user_by_id(1)
    print("our user : ", user)

    quiz = await mysql_orm.create_quiz(date=datetime.datetime.now(), difficulty=1, quiz_type="type", quiz_category=1)
    quiz = await mysql_orm.get_quiz_by_id(1)
    print("our quiz linked to the user : ", quiz)

    await mysql_orm.create_user_quiz(user=user, quiz=quiz)

    # await SomeModel.create(tournament_id=the_tournament.pk) on peut aussi créer un model juste avec la ref FK

    user_user_quizzes = await user.user_quizzes.all()
    print("all the user_quizzes we find for this user : ", user_user_quizzes)

    for user_quizzes in user_user_quizzes:
        await user_quizzes.fetch_related('quiz')
        quiz_ = user_quizzes.quiz
        print("Quiz linked to the user got from user_quizzes : ", quiz_)

    await mysql_orm.close()


async def test2():
    mysql_orm = await MysqlOrm.get_instance()

    user = await mysql_orm.get_user_by_id(1)

    quiz = await mysql_orm.get_quiz_by_id(1)

    question = await mysql_orm.create_question(title="title")

    answer_correct = await mysql_orm.create_answer(question=question, title="title", is_correct=True)
    answer_not_correct = await mysql_orm.create_answer(question=question, title="title", is_correct=False)

    await mysql_orm.create_user_answers(user=user, quiz=quiz, answer=answer_correct, answer_delay=0)


async def test_m2m_fields():
    mysql_orm = await MysqlOrm.get_instance()

    user1 = await mysql_orm.create_user(user_oauth_token="test_auth1")
    user2 = await mysql_orm.create_user(user_oauth_token="test_auth2")
    user3 = await mysql_orm.create_user(user_oauth_token="test_auth3")

    quiz1 = await mysql_orm.create_quiz(date=datetime.datetime.now(), difficulty=1, quiz_type="type", quiz_category=1)
    quiz2 = await mysql_orm.create_quiz(date=datetime.datetime.now(), difficulty=1, quiz_type="type", quiz_category=2)
    quiz3 = await mysql_orm.create_quiz(date=datetime.datetime.now(), difficulty=1, quiz_type="type", quiz_category=3)

    user1_quizzes = await user1.quizzes.all()
    print(user1_quizzes)

    quiz1_users = await quiz1.users.all()
    print(quiz1_users)

    await user1.quizzes.add(quiz1)
    await user1.quizzes.add(quiz2)
    await quiz1.users.add(user3)

    user1_quizzes = await user1.quizzes.all()
    print(user1_quizzes)

    quiz1_users = await quiz1.users.all()
    print(quiz1_users)


async def test_m2m_methods():
    mysql_orm = await MysqlOrm.get_instance()

    question1 = await mysql_orm.create_question(title="question1")
    question2 = await mysql_orm.create_question(title="question2")
    question3 = await mysql_orm.create_question(title="question3")

    quiz1 = await mysql_orm.create_quiz(date=datetime.datetime.now(), difficulty=1, quiz_type="type", quiz_category=1)
    quiz2 = await mysql_orm.create_quiz(date=datetime.datetime.now(), difficulty=1, quiz_type="type", quiz_category=2)
    quiz3 = await mysql_orm.create_quiz(date=datetime.datetime.now(), difficulty=1, quiz_type="type", quiz_category=3)

    quiz1_questions = await quiz1.questions.all()
    print(quiz1_questions)

    question1_quizzes = await question1.quizzes.all()
    print(question1_quizzes)

    await mysql_orm.add_m2m_quiz_question(quiz1, question1)

    quiz1_questions = await quiz1.questions.all()
    print(quiz1_questions)

    question1_quizzes = await question1.quizzes.all()
    print(question1_quizzes)


async def populate():
    pass



if __name__ == "__main__":
    run_async(test_m2m_methods())
