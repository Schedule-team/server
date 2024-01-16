import lxml.html
import time
import datetime
import requests
import json

from django.core.management.base import BaseCommand, CommandError, CommandParser
from course.models import *


def access_token() -> str:
    r = requests.get("https://catalog.ustc.edu.cn/get_token")
    return r.json()["access_token"]


def run():
    semesters = Semester.objects.all().order_by("start_date").reverse()
    for semester in semesters:
        print(semester)
        try:
            r = requests.get(
                f"http://catalog.ustc.edu.cn/api/teach/exam/list/{semester.jw_id}?access_token={access_token()}"
            )
            j = r.json()
        except:
            print(r.text)
            print("Failed to fetch exams")
            continue
        for json in j:
            # print(json)
            date = json["examDate"][:10]  # 2021-09-13 (UTC+8)
            start_time = json["startTime"]  # 1555 -> 15:55 (UTC+8)
            end_time = json["endTime"]  # 1640 -> 16:40 (UTC+8)

            # convert to djano datetime:
            start_time = datetime.datetime.strptime(
                f"{date} {start_time // 100}:{start_time % 100} +0800", "%Y-%m-%d %H:%M %z"
            ).astimezone(datetime.timezone.utc)
            end_time = datetime.datetime.strptime(
                f"{date} {end_time // 100}:{end_time % 100}", "%Y-%m-%d %H:%M"
            ).astimezone(datetime.timezone.utc)

            locations = []
            description = ""
            if "examRooms" in json:
                for location_json in json["examRooms"]:
                    if "id" in location_json and Location.objects.filter(jw_id=location_json["id"]).exists():
                        locations.append(Location.objects.get(
                            jw_id=location_json["id"])
                        )
                    else:
                        if description == "":
                            description = f"Location: {location_json['room']}"
                        else:
                            description += f", {location_json['room']}"

            if "lesson" not in json:
                continue

            type = json["examMode"]
            if type == None:
                type = ""

            e, _ = Lesson.Exam.objects.update_or_create(
                jw_id=json["id"],
                #
                lesson_info=Lesson.objects.get(jw_id=json["lesson"]["id"]),
                type=type,
                #
                start_time=start_time,
                end_time=end_time,
                description=description,
            )

            e.locations.set(locations)

            print(f"Updated {e}")


class Command(BaseCommand):
    help = "Fetches courses from USTC JW"

    def add_arguments(self, parser):
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        run()
