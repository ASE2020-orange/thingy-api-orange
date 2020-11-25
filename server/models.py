from tortoise.models import Model
from tortoise import fields


class Users(Model):
    id = fields.IntField(pk=True)
    user_oauth_token = fields.CharField(255)

    def __str__(self):
        return f"User {self.id}: {self.user_oauth_token}"


class Quizzes(Model):
    id = fields.IntField(pk=True)
    date = fields.DateField()
    difficulty = fields.IntField()
    quiz_type = fields.CharField(255)
    quiz_category = fields.CharField(255)

    def __str__(self):
        return f"Quiz {self.id}: {self.date}, {self.difficulty}, {self.quiz_type}, {self.quiz_category}"


class Questions(Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(255)
    question_type = fields.IntField()

    def __str__(self):
        return f"Question {self.id}: {self.title}, {self.question_type}"


class Answers(Model):
    id = fields.IntField(pk=True)
    question = fields.ForeignKeyField('models.Questions', related_name='question')
    title = fields.CharField(255)
    is_correct = fields.BooleanField()

    def __str__(self):
        return f"Answer {self.id}: {self.question.id}, {self.title}, {self.is_correct}"


class UserQuizzes(Model):
    user = fields.ForeignKeyField('models.Users', related_name='user_quizzes')
    quiz = fields.ForeignKeyField('models.Quizzes', related_name='user_quizzes')

    def __str__(self):
        return f"UserQuizz user : {self.user.id}, quiz : {self.quiz.id}"


class UserAnswers(Model):
    user = fields.ForeignKeyField('models.Users', related_name='user_answers')
    quiz = fields.ForeignKeyField('models.Quizzes', related_name='user_answers')
    answer = fields.ForeignKeyField('models.Answers', related_name='user_answers')
    answer_delay = fields.IntField()

    def __str__(self):
        return f"UserAnswers user : {self.user.id}, quiz : {self.quiz.id}, answer : {self.answer.id}, {answer_delay}"


class QuizQuestions(Model):
    quiz = fields.ForeignKeyField('models.Quizzes', related_name='quiz_questions')
    question = fields.ForeignKeyField('models.Questions', related_name='quiz_questions')

    def __str__(self):
        return f"QuizQuestions quiz : {self.quiz.id}, question : {self.question.id}"
