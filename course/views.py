from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.core.serializers import serialize
from django.forms.models import model_to_dict

from .models import *


def course_view(request, id):
    course = get_object_or_404(Course, id=id)
    lessons = get_list_or_404(Lesson, course=course)
    return render(
        request,
        "course.html",
        {
            "course": course,
            "lessons": lessons
        },
    )


def lesson_view(request, id):
    lesson = get_object_or_404(Lesson, id=id)
    lectures = Lesson.Lecture.objects.filter(lesson_info=lesson).order_by("start_time").reverse()
    exams = Lesson.Exam.objects.filter(lesson_info=lesson)
    return render(
        request,
        "lesson.html",
        {
            "lesson": lesson,
            "lectures": lectures,
            "exams": exams
        },
    )

def teacher_view(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    return render(
        request,
        "teacher.html",
        {
            "teacher": teacher
        },
    )