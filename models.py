import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *


DATABASE = MySQLDatabase('heroku_a29477c67a930cc', user='bed8bf4465c7c1', passwd='e8920cbb', host='eu-cdbr-west-02.cleardb.net')


class Article(Model):
    title = CharField(max_length=255)
    body = TextField()
    author = CharField(max_length=255)
    create_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE
        order_by = ('-create_date',)


class User(UserMixin, Model):
    username = CharField(max_length=30, unique=True)
    email = CharField(max_length=100, unique=True)
    password = CharField(max_length=100)
    register_date = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = DATABASE

    @classmethod
    def create_user(cls, username, email, password):
        try:
            with DATABASE.transaction():
                cls.create(email=email, username=username, password=generate_password_hash(password))
        except IntegrityError:
            raise ValueError('User already exists')


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([Article, User], safe=True)
    DATABASE.close()
