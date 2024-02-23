import datetime
import lxml.html
import requests
import time
from json import loads
from glom import glom
from django.core.management.base import BaseCommand, CommandError
from course.models import *


semesters = {}


def update_semesters():
    global semesters

    r = requests.get("https://catalog.ustc.edu.cn/get_token")
    token = r.json()["access_token"]
    r = requests.get(
        f"https://catalog.ustc.edu.cn/api/teach/semester/list?access_token={token}"
    )
    for semester in r.json():
        s, _ = Semester.objects.update_or_create(
            jw_id=semester["id"],
            #
            defaults={
                "code": semester["code"],
                "name": semester["nameZh"],
                "start_date": datetime.datetime.strptime(semester["start"], "%Y-%m-%d"),
                "end_date": datetime.datetime.strptime(semester["end"], "%Y-%m-%d"),
            }
        )
        semesters[s.jw_id] = s
        # print("Added " + s.name)


def handle_course(json):
    c, _ = Course.objects.update_or_create(
        code=json["code"],
        #
        jw_id=json["id"],
        #
        defaults={
            "name": glom(json, "nameZh", default=""),
            "period": glom(json, "periodInfo.total", default=""),
            "credits": glom(json, "credits", default=""),
            "type_base": glom(json, "courseCategory.nameZh", default=""),
            "type_teaching_method": glom(json, "courseType.nameZh", default=""),
            "type_join_type": glom(json, "courseGradation.nameZh", default=""),
            "type_level": glom(json, "education.nameZh", default=""),
            "open_department": glom(json, "defaultOpenDepart.simpleNameZh", default=""),
            "exam_type": glom(json, "defaultExamMode.nameZh", default=""),
            "grading_type": glom(json, "scoreMarkStyle.name", default=""),
            "description": glom(json, "introduction", default=""),
        },
    )
    return c


def handle_teacher(json):
    t, _ = Teacher.objects.update_or_create(
        jw_id=glom(json, "teacher.person.id", default=""),
        defaults={
            "name": glom(json, "teacher.person.nameZh", default=""),
            "email": glom(json, "teacher.person.contactInfo.email", default=""),
            "office_location": glom(json, "teacher.person.contactInfo.address", default=""),
            "homepage_url": glom(json, "teacher.person.personalPage", default=""),
        }
    )

    return t


def handle_lesson(json, semester_id):
    course = handle_course(json["course"])
    teachers = [
        handle_teacher(teacher_json) for teacher_json in json["teacherAssignmentList"]
    ]
    l, _ = Lesson.objects.update_or_create(
        jw_id=json["id"],
        #
        defaults={
            "semester": semesters[semester_id],
            "course": course,
            #
            "code": glom(json, "code", default=""),
            "campus": glom(json, "campus.nameZh", default=""),
            "start_week": glom(json, "scheduleStartWeek", default=""),
            "end_week": glom(json, "scheduleEndWeek", default=""),
            "schedule_text": glom(
                json, "scheduleText.dateTimePlacePersonText.textZh", default=""
            ),
            "homepage_url": "",
        },
    )
    l.teachers.set(teachers)
    course.semesters.add(semesters[semester_id])
    return l


def handle_each_semester_raw(raw, semester_id):
    obj = loads(raw)
    for lesson in obj["data"]:
        lecture = handle_lesson(lesson, semester_id)
        print("Added " + lecture.course.name + " " + lecture.code)


def run(cookie, std_id):
    update_semesters()
    headers = {
        "cookie": cookie,
        "accept": "application/json, text/javascript, */*; q=0.01",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/102.0.0.0 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
        "authority": "jw.ustc.edu.cn",
        "referer": f"https://jw.ustc.edu.cn/for-std/lesson-search/index/{std_id}",
    }

    index_url = f"https://jw.ustc.edu.cn/for-std/lesson-search/index/{std_id}"

    r = requests.get(index_url, headers=headers)
    doc = lxml.html.fromstring(r.text)
    options = doc.xpath('//select[@id="semester"]/option')
    if len(options) == 0:
        raise CommandError(
            "Semesters not found, please check whether cookie is valid")

    print("Found " + str(len(options)) + " semesters")

    for option in options:
        # if input("Download " + option.text + "? (y/n)") != "y":
        #     continue
        print("Downloading " + option.text)
        semester_id = option.attrib["value"]
        lesson_url = f"""
        https://jw.ustc.edu.cn/for-std/lesson-search/semester/{semester_id}/search/{std_id}?courseCodeLike=&codeLike=&educationAssoc=&courseNameZhLike=&teacherNameLike=&schedulePlace=&classCodeLike=&courseTypeAssoc=&classTypeAssoc=&campusAssoc=&teachLangAssoc=&roomTypeAssoc=&examModeAssoc=&requiredPeriodInfo.totalGte=&requiredPeriodInfo.totalLte=&requiredPeriodInfo.weeksGte=&requiredPeriodInfo.weeksLte=&requiredPeriodInfo.periodsPerWeekGte=&requiredPeriodInfo.periodsPerWeekLte=&limitCountGte=&limitCountLte=&majorAssoc=&majorDirectionAssoc=&queryPage__=1%2C100000&_=1656750
        """
        for repeat in range(5):
            try:
                r = requests.get(lesson_url, headers=headers)
                break
            except Exception as e:
                print(e)
                print("Retrying...")
                time.sleep(1)

        handle_each_semester_raw(r.text, semester_id)


class Command(BaseCommand):
    help = "Fetches courses from USTC JW"

    def add_arguments(self, parser):
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        cookie = input(
            "Login to https://jw.ustc.edu.cn/ and copy the cookies here:"
        )
        if not cookie:
            raise CommandError("Cookie is empty")

        std_id = input("Look out for a integer in requests, paste it here:")
        if not std_id.isdigit():
            raise CommandError("Student ID is invalid")

        run(cookie, std_id)
