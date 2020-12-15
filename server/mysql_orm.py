from tortoise import Tortoise, run_async
from models import *
import datetime


class MysqlOrm:
    get_instance_used = False
    instance = None

    @staticmethod
    async def get_instance(user, pwd, host, port, db):
        if MysqlOrm.instance == None:
            MysqlOrm.get_instance_used = True
            MysqlOrm()

            # TODO read these from config file
            await Tortoise.init(
                db_url=f'mysql://{user}:{pwd}@{host}:{port}/{db}',
                modules={'models': ['models']}
            )

            await Tortoise.generate_schemas()
        return MysqlOrm.instance


    def __init__(self):
       if MysqlOrm.get_instance_used == False or MysqlOrm.instance != None:
          raise Exception("This class is a singleton, use the get_instance method !")
       else:
          MysqlOrm.instance = self


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


    async def create_user_quiz(self, user, quiz):
        user_quiz = UserQuizzes(user=user, quiz=quiz)
        await user_quiz.save()


    async def create_user_answers(self, user, quiz, answer, answer_delay):
        user_answer = UserAnswers(user=user, quiz=quiz, answer=answer, answer_delay=answer_delay)
        await user_answer.save()


    async def get_all_users(self):
        return await Users.all()


    async def get_all_quizzes(self):
        return await Quizzes.all()


    async def get_all_questions(self):
        return await Questions.all()


    async def get_all_answers(self):
        return await Answers.all()


    async def get_user_by_id(self, id):
        return await Users.filter(id=id).get()
    
    async def get_user_by_oauth_id(self, id):
        return await Users.filter(user_oauth_token=id).get()


    async def get_quiz_by_id(self, id):
        return await Quizzes.filter(id=id).get()


    async def get_question_by_id(self, id):
        return await Questions.filter(id=id).get()


    async def get_answer_by_id(self, id):
        return await Answers.filter(id=id).get()


    async def get_answers_of_user(self, user_id):
        answers = []

        user = await self.get_user_by_id(user_id)
        user = user[0]

        user_user_answers = await user.user_answers.all()
        for user_user_answer in user_user_answers:
            await user_user_answer.fetch_related('answer')
            answer_of_user = user_user_answer.answer
            answers.append(answer_of_user)

        return answers

    async def get_answers_of_question(self, question_id):
        return await Answers.filter(question=await self.get_question_by_id(question_id))


async def test():
    mysql_orm = await MysqlOrm.get_instance('root','mysql', 'localhost', 3306, 'test')

    user = await mysql_orm.create_user(user_oauth_token="test_auth")
    user = await mysql_orm.get_user_by_id(1)
    user = user[0]
    print("our user : ", user)

    quiz = await mysql_orm.create_quiz(date=datetime.datetime.now(), difficulty=1, quiz_type="type", quiz_category="category")
    quiz = await mysql_orm.get_quiz_by_id(1)
    quiz = quiz[0]
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
    user = user[0]

    quiz = await mysql_orm.get_quiz_by_id(1)
    quiz = quiz[0]

    question = await mysql_orm.create_question(title="title")

    answer_correct = await mysql_orm.create_answer(question=question, title="title", is_correct=True)
    answer_not_correct = await mysql_orm.create_answer(question=question, title="title", is_correct=False)

    await mysql_orm.create_user_answers(user=user, quiz=quiz, answer=answer_correct, answer_delay=0)


async def populate():
    pass



if __name__ == "__main__":
    run_async(test())
