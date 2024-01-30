from django.shortcuts import render, get_object_or_404, get_list_or_404

from .models import *


def index_view(request):
    return render(request, "index.html")


def course_all(request):
    PAGE_SIZE = 20

    pn = int(request.GET.get("pn", 1) or 1)
    name = request.GET.get("name", "")
    # semester_id = request.GET.get("semester", "")

    courses = list(Course.objects.all())

    if len(name):
        name = name.strip()
        courses = list(filter(lambda course: name in course.name or name in course.code, courses))

    # if len(semester_id):
    #     semester_id = int(semester_id)
    #     course = filter(
    #         lambda course: course.semester.id == semester_id,
    #         course,
    #     )

    total = len(courses)
    courses = courses[(int(pn) - 1) * PAGE_SIZE: int(pn) * PAGE_SIZE]

    # semesters = sorted(list(Semester.objects.all()),
    #                    key=lambda x: x.name, reverse=True)

    return render(
        request,
        "course_all.html",
        {
            "courses": courses,
            "pn": int(pn),
            "pn_max": int(total / PAGE_SIZE) + 1,
            "total": total,
            "name": name,
            # "semesters": semesters,
            # "semester_id": semester_id
        },
    )


def course_view(request, id):
    course = get_object_or_404(Course, id=id)
    lessons = get_list_or_404(Lesson, course=course)
    semesters = sorted(list(dict.fromkeys(
        list(map(lambda lesson: lesson.semester, lessons)))), key=lambda x: x.name, reverse=True)

    name = request.GET.get("name", "")
    semester_id = request.GET.get("semester", "")

    if len(name):
        name = name.strip()
        lessons = filter(
            lambda lesson: name in lesson.code or name in lesson.teachers_name,
            lessons,
        )

    if len(semester_id):
        semester_id = int(semester_id)
        lessons = filter(
            lambda lesson: lesson.semester.id == semester_id,
            lessons,
        )
    else:
        semester_id = ""

    return render(
        request,
        "course.html",
        {
            "course": course,
            "lessons": lessons,
            "name": name,
            "semester_id": semester_id,
            "semesters": semesters
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

    teachers = list(lesson.teachers.all())

    teacher_id = ""
    if teachers:
        teacher_id = teachers[0].id

    return render(
        request,
        "lesson.html",
        {
            "lesson": lesson,
            "lectures": lectures,
            "exams": exams,
            "teacher_id": teacher_id,
        },
    )


def teacher_view(request, id):
    teacher = get_object_or_404(Teacher, id=id)
    return render(
        request,
        "teacher.html",
        {"teacher": teacher},
    )
