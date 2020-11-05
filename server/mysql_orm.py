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
                db_url='mysql://root:mysql@localhost:3306/thingy_quizz',
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


    async def create_user(self):
        user = Users(user_oauth_token='python')
        await user.save()


    async def create_quiz(self):
        quiz = Quizzes(date=datetime.datetime.now(), difficulty=1, quiz_type="type", quiz_category="category")
        await quiz.save()


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

    get_all_test = await mysql_orm.get_all_users()
    for elem in get_all_test:
        print(elem)

    get_by_id_test = await mysql_orm.get_answer_by_id(1)
    for elem in get_by_id_test:
        print(elem)

    await mysql_orm.close()



if __name__ == "__main__":
    run_async(test())
