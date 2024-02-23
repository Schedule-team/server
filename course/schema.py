import graphene
from graphene import relay, ObjectType
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .models import *


class SemesterNode(DjangoObjectType):
    class Meta:
        model = Semester
        interfaces = (relay.Node,)
        filter_fields = [
            "semester_courses",
            "semester_lessons",
        ]


class CourseNode(DjangoObjectType):
    class Meta:
        model = Course
        interfaces = (relay.Node,)
        filter_fields = [
            "course_lessons",
        ]


class TeacherNode(DjangoObjectType):
    class Meta:
        model = Teacher
        interfaces = (relay.Node,)
        filter_fields = [
            "teacher_lessons",
        ]


class LocationNode(DjangoObjectType):
    class Meta:
        model = Location
        interfaces = (relay.Node,)
        filter_fields = []


class LessonNode(DjangoObjectType):
    class Meta:
        model = Lesson
        interfaces = (relay.Node,)
        filter_fields = [
            "lesson_lectures",
            "lesson_exams",
            "lesson_homeworks",
        ]


class LectureNode(DjangoObjectType):
    class Meta:
        model = Lecture
        interfaces = (relay.Node,)
        filter_fields = []


class ExamNode(DjangoObjectType):
    class Meta:
        model = Exam
        interfaces = (relay.Node,)
        filter_fields = []


class HomeworkNode(DjangoObjectType):
    class Meta:
        model = Homework
        interfaces = (relay.Node,)
        filter_fields = []


class Query(graphene.ObjectType):
    semester = relay.Node.Field(SemesterNode)
    all_semesters = DjangoFilterConnectionField(SemesterNode)
    course = relay.Node.Field(CourseNode)
    all_courses = DjangoFilterConnectionField(CourseNode)
    teacher = relay.Node.Field(TeacherNode)
    all_teachers = DjangoFilterConnectionField(TeacherNode)
    location = relay.Node.Field(LocationNode)
    all_locations = DjangoFilterConnectionField(LocationNode)
    lesson = relay.Node.Field(LessonNode)
    all_lessons = DjangoFilterConnectionField(LessonNode)
    lecture = relay.Node.Field(LectureNode)
    all_lectures = DjangoFilterConnectionField(LectureNode)
    exam = relay.Node.Field(ExamNode)
    all_exams = DjangoFilterConnectionField(ExamNode)
    homework = relay.Node.Field(HomeworkNode)
    all_homeworks = DjangoFilterConnectionField(HomeworkNode)


schema = graphene.Schema(query=Query)
