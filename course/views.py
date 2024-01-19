from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.core.serializers import serialize
from django.forms.models import model_to_dict

from .models import *


def course_view(request, id):
    course = get_object_or_404(Course, id=id)
    lessons = get_list_or_404(Lesson, course=course)

    search = request.GET.get("search", "")

    if search:
        lessons = [
            lesson
            for lesson in lessons
            if (search in lesson.code or search in lesson.teachers_name)
        ]
    else:
        search = ""

    return render(
        request,
        "course.html",
        {
            "course": course,
            "lessons": lessons,
            "search": search,
        },
    )


def lesson_view(request, id):
    lesson = get_object_or_404(Lesson, id=id)
    lectures = (
        Lesson.Lecture.objects.filter(lesson_info=lesson)
        .order_by("start_time")
        .reverse()
    )
    exams = Lesson.Exam.objects.filter(lesson_info=lesson)

    teachers = lesson.teachers.all()
    if len(teachers) == 0:
        have_teacher = False
        teacher_name = ""
        teacher_id = ""
    else:
        have_teacher = True
        teacher_name = teachers[0].name
        teacher_id = teachers[0].id

    return render(
        request,
        "lesson.html",
        {
            "lesson": lesson,
            "lectures": lectures,
            "exams": exams,
            "have_teacher": have_teacher,
            "teacher_id": teacher_id,
            "teacher_name": teacher_name,
        },
    )


def teacher_view(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    return render(
        request,
        "teacher.html",
        {"teacher": teacher},
    )
