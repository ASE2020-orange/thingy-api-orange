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
    question_id = fields.IntField()
    title = fields.CharField(255)
    is_correct = fields.BooleanField()

    def __str__(self):
        return f"Answer {self.id}: {self.question_id}, {self.title}, {self.is_correct}"
