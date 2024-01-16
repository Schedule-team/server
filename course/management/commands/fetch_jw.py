import lxml.html
import time
import datetime
import requests
import json

from django.core.management.base import BaseCommand, CommandError, CommandParser
from course.models import *

# Update semesters: (before any input are given)
r = requests.get("https://catalog.ustc.edu.cn/get_token")
token = r.json()["access_token"]
r = requests.get(
    f"https://catalog.ustc.edu.cn/api/teach/semester/list?access_token={token}"
)
semesters = {}
for semester in r.json():
    s, _ = Semester.objects.update_or_create(
        jw_id=semester["id"],
        #
        code=semester["code"],
        name=semester["nameZh"],
        start_date=datetime.datetime.strptime(semester["start"], "%Y-%m-%d"),
        end_date=datetime.datetime.strptime(semester["end"], "%Y-%m-%d"),
    )
    semesters[s.jw_id] = s


def handle_course(json):
    # the following code is to prevent "NoneType cannot be subscripted" error
    # a pep around optional chaining may relieve such issues, but for now we have to do this
    if not json["courseCategory"]:
        json["courseCategory"] = {"nameZh": ""}
    if not json["courseType"]:
        json["courseType"] = {"nameZh": ""}
    if not json["courseGradation"]:
        json["courseGradation"] = {"nameZh": ""}
    if not json["education"]:
        json["education"] = {"nameZh": ""}
    if not json["defaultOpenDepart"]:
        json["defaultOpenDepart"] = {"simpleNameZh": ""}
    if not json["defaultExamMode"]:
        json["defaultExamMode"] = {"nameZh": ""}
    if not json["scoreMarkStyle"]:
        json["scoreMarkStyle"] = {"name": ""}

    c, _ = Course.objects.update_or_create(
        code=json["code"],
        #
        jw_id=json["id"],
        #
        name=json["nameZh"],
        period=json["periodInfo"]["total"],
        credits=json["credits"],
        #
        type_base=json["courseCategory"]["nameZh"],
        type_teaching_method=json["courseType"]["nameZh"],
        type_join_type=json["courseGradation"]["nameZh"],
        type_level=json["education"]["nameZh"],
        #
        open_department=json["defaultOpenDepart"]["simpleNameZh"],
        #
        exam_type=json["defaultExamMode"]["nameZh"],
        grading_type=json["scoreMarkStyle"]["name"],
        #
        description=json["introduction"],
    )
    return c


def handle_teacher(json):
    t, _ = Teacher.objects.update_or_create(
        jw_id=json["teacher"]["person"]["id"],
        #
        name=json["teacher"]["person"]["nameZh"],
        email=json["teacher"]["person"]["contactInfo"]["email"],
        office_location=json["teacher"]["person"]["contactInfo"]["address"],
        homepage_url=json["teacher"]["person"]["personalPage"],
    )
    return t


def handle_lesson(json, semester_id):
    if not json["campus"]:
        json["campus"] = {"nameZh": ""}
    if not json["scheduleText"] or not json["scheduleText"]["dateTimePlacePersonText"]:
        json["scheduleText"] = {"dateTimePlacePersonText": {"textZh": ""}}

    course = handle_course(json["course"])
    teachers = [
        handle_teacher(teacher_json) for teacher_json in json["teacherAssignmentList"]
    ]
    l, _ = Lesson.objects.update_or_create(
        jw_id=json["id"],
        #
        semester=semesters[semester_id],
        course=course,
        #
        code=json["code"],
        campus=json["campus"]["nameZh"],
        start_week=json["scheduleStartWeek"],
        end_week=json["scheduleEndWeek"],
        schedule_text=json["scheduleText"]["dateTimePlacePersonText"]["textZh"],
        homepage_url="",
    )
    l.teachers.set(teachers)
    return l


def handle(raw, semester_id):
    obj = json.loads(raw)
    for lesson in obj["data"]:
        l = handle_lesson(lesson, semester_id)
        print("Added " + l.course.name + " " + l.code)


def run(cookie, std_id):
    headers = {
        "cookie": cookie,
        "accept": "application/json, text/javascript, */*; q=0.01",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
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
        for repeat in range(5):
            try:
                print("Downloading " + option.text)
                semester_id = option.attrib["value"]
                lesson_url = f"https://jw.ustc.edu.cn/for-std/lesson-search/semester/{semester_id}/search/{std_id}?courseCodeLike=&codeLike=&educationAssoc=&courseNameZhLike=&teacherNameLike=&schedulePlace=&classCodeLike=&courseTypeAssoc=&classTypeAssoc=&campusAssoc=&teachLangAssoc=&roomTypeAssoc=&examModeAssoc=&requiredPeriodInfo.totalGte=&requiredPeriodInfo.totalLte=&requiredPeriodInfo.weeksGte=&requiredPeriodInfo.weeksLte=&requiredPeriodInfo.periodsPerWeekGte=&requiredPeriodInfo.periodsPerWeekLte=&limitCountGte=&limitCountLte=&majorAssoc=&majorDirectionAssoc=&queryPage__=1%2C100000&_=1656750"

                r = requests.get(lesson_url, headers=headers)
            except Exception as e:
                print(e)
                print("Retrying...")
                time.sleep(1)

            handle(r.text, semester_id)
            break


class Command(BaseCommand):
    help = "Fetches courses from USTC JW"

    def add_arguments(self, parser):
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        cookie = input(
            "Login to https://jw.ustc.edu.cn/ and copy the cookies here:")
        if not cookie:
            raise CommandError("No cookies provided")
        std_id = input("Look out for a integer in requests, paste it here:")
        run(cookie, std_id)
