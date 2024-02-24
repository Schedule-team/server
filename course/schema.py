import strawberry
import strawberry_django
from strawberry_django.optimizer import DjangoOptimizerExtension

from .types import *


@strawberry.type
class Query:
    @strawberry.field
    def hello() -> str:
        return "Hello, world!"

    semesters: list[Semester] = strawberry_django.field()
    courses: list[Course] = strawberry_django.field()
    teachers: list[Teacher] = strawberry_django.field()
    locations: list[Location] = strawberry_django.field()
    lessons: list[Lesson] = strawberry_django.field()
    lectures: list[Lecture] = strawberry_django.field()
    exams: list[Exam] = strawberry_django.field()
    homeworks: list[Homework] = strawberry_django.field()


@strawberry.type
class Mutation:
    pass
