from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.core.serializers import serialize
from django.forms.models import model_to_dict

from .models import *


def add_prefix_to_dict_keys(prefix, dict):
    return {prefix + key: value for key, value in dict.items()}


def model_to_dict_for_lesson(lesson):
    lesson_dict = model_to_dict(
        lesson, fields=[field.name for field in lesson._meta.fields]
    )
    # add related course information to lesson, dicrtionary union:
    return {
        **lesson_dict,
        **add_prefix_to_dict_keys("course_", model_to_dict(lesson.course)),
        **add_prefix_to_dict_keys("semester_", model_to_dict(lesson.semester)),
    }


def query_course_all(request):
    courses = Course.objects.all()
    return JsonResponse({"courses": list(courses.values())})


def query_course(request, id):
    course = get_object_or_404(Course, id=id)
    return JsonResponse({"course": model_to_dict(course)})


def query_teacher_all(request):
    teachers = Teacher.objects.all()
    return JsonResponse({"teachers": list(teachers.values())})


def query_teacher(request, id):
    teacher = get_object_or_404(Teacher, id=id)

    # fetch all lesson that this teacher teaches, which have a many-to-many relationship with Teacher
    lessons = teacher.lesson_set.all()

    lessons_data = [model_to_dict_for_lesson(lesson) for lesson in lessons]

    return JsonResponse(
        {
            "teacher": model_to_dict(teacher),
            "lessons": lessons_data,
        }
    )


def query_semester_all(request):
    semesters = Semester.objects.all()
    return JsonResponse({"semesters": list(semesters.values())})


def query_semester(request, id):
    semester = get_object_or_404(Semester, id=id)
    return JsonResponse({"semester": model_to_dict(semester)})


def query_lesson_all(request):
    lessons = Lesson.objects.all()
    return JsonResponse({"lessons": list(lessons.values())})


def query_lesson(request, id):
    lesson = get_object_or_404(Lesson, id=id)
    return JsonResponse({"lesson": model_to_dict_for_lesson(lesson)})
