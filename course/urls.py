from django.urls import path
from . import api

urlpatterns = [
    path("api/course/", api.query_course_all, name="index"),
    path("api/course/<int:id>", api.query_course, name="course"),
    path("api/lesson/", api.query_lesson_all, name="lesson"),
    path("api/lesson/<int:id>", api.query_lesson, name="lesson"),
    path("api/teacher/", api.query_teacher_all, name="teacher"),
    path("api/teacher/<int:id>", api.query_teacher, name="teacher"),
    path("api/semester/", api.query_semester_all, name="semester"),
    path("api/semester/<int:id>", api.query_semester, name="semester"),
]