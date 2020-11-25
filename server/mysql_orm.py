from tortoise import Tortoise, run_async
from models import *
import datetime


class MysqlOrm:
    get_instance_used = False
    instance = None

    @staticmethod
    async def get_instance():
        if MysqlOrm.instance == None:
            MysqlOrm.get_instance_used = True
            MysqlOrm()

            # TODO read these from config file
            await Tortoise.init(
                db_url='mysql://root:mysql@localhost:3306/test',
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


    async def create_user_quiz(self, user, quiz):
        user_quiz = UserQuizzes(user=user, quiz=quiz)
        await user_quiz.save()


    async def create_question(self):
        question = Questions(title="title", question_type=1)
        await question.save()


    async def create_answer(self):
        answer = Answers(title="title", question_id=1, is_correct=True)
        await answer.save()


    async def get_all_users(self):
        return await Users.all()


    async def get_all_quizzes(self):
        return await Quizzes.all()


    async def get_all_questions(self):
        return await Questions.all()


    async def get_all_answers(self):
        return await Answers.all()


    async def get_user_by_id(self, id):
        return await Users.filter(id=id)


    async def get_quiz_by_id(self, id):
        return await Quizzes.filter(id=id)


    async def get_question_by_id(self, id):
        return await Questions.filter(id=id)


    async def get_answer_by_id(self, id):
        return await Answers.filter(id=id)



async def test():
    mysql_orm = await MysqlOrm.get_instance()

    # user = await mysql_orm.create_user(user_oauth_token="test_auth")
    user = await mysql_orm.get_user_by_id(11)
    user = user[0]
    print("our user : ", user)

    # quiz = await mysql_orm.create_quiz(date=datetime.datetime.now(), difficulty=1, quiz_type="type", quiz_category="category")
    quiz = await mysql_orm.get_quiz_by_id(6)
    quiz = quiz[0]
    print("our quiz linked to the user : ", quiz)

    # await mysql_orm.create_user_quiz(user=user, quiz=quiz)
    # await SomeModel.create(tournament_id=the_tournament.pk) on peut aussi créer un model juste avec la ref FK

    user_user_quizzes = await user.user_quizzes.all()
    print("all the user_quizzes we find for this user : ", user_user_quizzes)

    for user_quizzes in user_user_quizzes:
        await user_quizzes.fetch_related('quiz')
        quiz_ = user_quizzes.quiz
        print("Quiz linked to the user got from user_quizzes : ", quiz_)

    await mysql_orm.close()



if __name__ == "__main__":
    run_async(test())
