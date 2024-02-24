import strawberry_django
from strawberry import auto

from . import models


@strawberry_django.type(models.Semester)
class Semester:
    id: auto
    jw_id: auto
    code: auto
    name: auto
    start_date: auto
    end_date: auto


@strawberry_django.type(models.Course)
class Course:
    id: auto
    jw_id: auto
    # semesters: 'Semester'
    code: auto
    name: auto
    period: auto
    credits: auto
    type_base: auto
    type_teaching_method: auto
    type_join_type: auto
    type_level: auto
    open_department: auto
    exam_type: auto
    grading_type: auto
    description: auto
    info: auto


@strawberry_django.type(models.Teacher)
class Teacher:
    id: auto
    jw_id: auto
    name: auto
    email: auto
    office_location: auto
    homepage_url: auto


@strawberry_django.type(models.Location)
class Location:
    id: auto
    jw_id: auto
    campus: auto
    building: auto
    room: auto


@strawberry_django.type(models.Lesson)
class Lesson:
    id: auto
    jw_id: auto
    semester: 'Semester'
    course: 'Course'
    # teacher: 'Teacher'
    code: auto
    campus: auto
    start_week: auto
    end_week: auto
    schedule_text: auto
    homepage_url: auto
    # notice_md_text


@strawberry_django.type(models.Lecture)
class Lecture:
    id: auto
    # jw_id: auto
    lesson: 'Lesson'
    location: 'Location'
    # teacher: 'Teacher'
    start_time: auto
    end_time: auto
    # history: auto


@strawberry_django.type(models.Exam)
class Exam:
    id: auto
    jw_id: auto
    lesson: 'Lesson'
    # location: 'Location'
    type: auto
    start_time: auto
    end_time: auto
    description: auto
    # history: auto


@strawberry_django.type(models.Homework)
class Homework:
    id: auto
    lesson: 'Lesson'
    description: auto
    deadline: auto
    created_at: auto
    updated_at: auto
    # history: auto
