from tortoise.models import Model
from tortoise import fields


class Users(Model):
    id = fields.IntField(pk=True)
    user_oauth_token = fields.CharField(255)
    quizzes = fields.ManyToManyField('models.Quizzes', related_name='users')
    answers = fields.ManyToManyField('models.Answers', related_name='users')

    def __str__(self):
        return f"User {self.id}: {self.user_oauth_token}"


class Quizzes(Model):
    id = fields.IntField(pk=True)
    date = fields.DateField()
    difficulty = fields.CharField(255)
    quiz_type = fields.CharField(255)
    quiz_category = fields.IntField()
    questions = fields.ManyToManyField('models.Questions', related_name='quizzes')

    def __str__(self):
        return f"Quiz {self.id}: {self.date}, {self.difficulty}, {self.quiz_type}, {self.quiz_category}"


class Questions(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(255)

    def __str__(self):
        return f"Question {self.id}: {self.title}"


class Answers(Model):
    id = fields.IntField(pk=True)
    question = fields.ForeignKeyField('models.Questions', related_name='answers')
    title = fields.CharField(255)
    is_correct = fields.BooleanField()

    def __str__(self):
        return f"Answer {self.id}: {self.question_id}, {self.title}, {self.is_correct}"


# class UserQuizzes(Model):
#     user = fields.ForeignKeyField('models.Users', related_name='user_quizzes')
#     quiz = fields.ForeignKeyField('models.Quizzes', related_name='user_quizzes')
#
#     def __str__(self):
#         return f"UserQuizz user : {self.user_id}, quiz : {self.quiz_id}"


class UserAnswers(Model):
    user = fields.ForeignKeyField('models.Users', related_name='user_answers')
    quiz = fields.ForeignKeyField('models.Quizzes', related_name='user_answers')
    answer = fields.ForeignKeyField('models.Answers', related_name='user_answers')
    answer_delay = fields.IntField()

    def __str__(self):
        return f"UserAnswers user : {self.user_id}, quiz : {self.quiz_id}, answer : {self.answer_id}, {self.answer_delay}"


# class QuizQuestions(Model):
#     quiz = fields.ForeignKeyField('models.Quizzes', related_name='quiz_questions')
#     question = fields.ForeignKeyField('models.Questions', related_name='quiz_questions')
#
#     def __str__(self):
#         return f"QuizQuestions quiz : {self.quiz_id}, question : {self.question_id}"
