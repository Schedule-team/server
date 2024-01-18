from django.urls import path
from . import api, views

urlpatterns = [
    path("api/course/", api.query_course_all, name="api_course_all"),
    path("api/course/<int:id>", api.query_course, name="api_course"),
    path("api/lesson/", api.query_lesson_all, name="api_lesson_all"),
    path("api/lesson/<int:id>", api.query_lesson, name="api_lesson"),
    path("api/teacher/", api.query_teacher_all, name="api_teacher_all"),
    path("api/teacher/<int:id>", api.query_teacher, name="api_teacher"),
    path("api/semester/", api.query_semester_all, name="api_semester_all"),
    path("api/semester/<int:id>", api.query_semester, name="api_semester"),
    #
    path("course/<int:id>", views.course_view, name="course"),
    path("lesson/<int:id>", views.lesson_view, name="lesson"),
    path("teacher/<int:id>", views.teacher_view, name="teacher"),
]
