import os

from django import forms
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from .models import *

# this would be set in .env file, loaded by docker-compose
CF_WORKER_CREDENTIAL = os.environ.get("CF_WORKER_CREDENTIAL")


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
    course = get_object_or_404(Course, jw_id=id)
    return JsonResponse({"course": model_to_dict(course)})


def query_teacher_all(request):
    teachers = Teacher.objects.all()
    return JsonResponse({"teachers": list(teachers.values())})


def query_teacher(request, id):
    teacher = get_object_or_404(Teacher, jw_id=id)

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
    semester = get_object_or_404(Semester, jw_id=id)
    return JsonResponse({"semester": model_to_dict(semester)})


def query_lesson_all(request):
    lessons = Lesson.objects.all()
    return JsonResponse({"lessons": list(lessons.values())})


def query_lesson(request, id):
    lesson = get_object_or_404(Lesson, jw_id=id)
    return JsonResponse({"lesson": model_to_dict_for_lesson(lesson)})


class CFEmailWorkerForm(forms.Form):
    credential = forms.CharField(max_length=100)
    id = forms.IntegerField()
    field = forms.CharField(max_length=100)
    value = forms.CharField(max_length=100)
    from_ = forms.EmailField()
    timestamp = forms.DateTimeField()


def cf_email_worker(request):
    """
    This function is called by Cloudflare worker

    Payload from CF worker:
    {
        "credential": "123456",
        "id": "123456",
        "field": "name",
        "value": "new name"
        "from": "xxx@xxx.xxx",
        "timestamp": "2021-01-01 00:00:00",
    }
    """

    form = CFEmailWorkerForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": "invalid form"})

    if form.cleaned_data["credential"] != CF_WORKER_CREDENTIAL:
        return JsonResponse({"error": "invalid credential"})

    id = form.cleaned_data["id"]
    lesson = get_object_or_404(Lesson, jw_id=id)

    field = form.cleaned_data["field"]
    value = form.cleaned_data["value"]

    if field == "notice":
        lesson.notice_md_text.update(
            text=value,
            last_modifed=form.cleaned_data["timestamp"],
            last_modified_by=form.cleaned_data["from"],
        )
    elif field == "homework":
        lesson.homework_md_text.update(
            text=value,
            last_modifed=form.cleaned_data["timestamp"],
            last_modified_by=form.cleaned_data["from"],
        )
    else:
        return JsonResponse({"error": "invalid field"})
