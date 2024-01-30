import asyncio
import datetime

import aiohttp
import tqdm
from django.core.management.base import BaseCommand, CommandError

from course.models import *

cookie = ""
headers = {}

GROUP_SIZE = 20
MAX_RETRIES = 5


async def handle_room(json) -> Location:
    l, _ = await Location.objects.aupdate_or_create(
        jw_id=json["id"],
        campus=json["building"]["campus"]["nameZh"],
        building=json["building"]["nameZh"],
        room=json["nameZh"],
    )
    return l


async def handle_lecture(json) -> Lesson.Lecture:
    # jw_id = json["id"]
    lesson = await Lesson.objects.aget(jw_id=json["lessonId"])

    date = json["date"]  # 2021-09-13 (UTC+8)
    start_time = json["startTime"]  # 1555 -> 15:55 (UTC+8)
    end_time = json["endTime"]  # 1640 -> 16:40 (UTC+8)

    # convert to djano datetime:
    start_time = datetime.datetime.strptime(
        f"{date} {start_time // 100}:{start_time % 100} +0800", "%Y-%m-%d %H:%M %z"
    ).astimezone(datetime.timezone.utc)
    end_time = datetime.datetime.strptime(
        f"{date} {end_time // 100}:{end_time % 100}", "%Y-%m-%d %H:%M"
    ).astimezone(datetime.timezone.utc)

    if json["room"]:
        l = await handle_room(json["room"])
    else:
        l = None
    lecture, _ = await Lesson.Lecture.objects.aupdate_or_create(
        # jw_id=jw_id,
        lesson_info=lesson,
        #
        start_time=start_time,
        end_time=end_time,
        #
        location=l,
    )
    if json["personId"]:
        await lecture.teachers.aset([await Teacher.objects.aget(jw_id=json["personId"])])


async def update_lessons(lesson_ids, semaphores, progress, session):
    async with semaphores:
        for i in range(MAX_RETRIES):
            try:
                data = {
                    "lessonIds": lesson_ids,
                }
                r = await session.post(
                    url="https://jw.ustc.edu.cn/ws/schedule-table/datum",
                    json=data,
                    headers=headers,
                )
                json = (await r.json())["result"]["scheduleList"]
                for sub_json in json:
                    await handle_lecture(sub_json)
                progress.update(len(lesson_ids))
                break
            except Exception as e:
                print(e)
                print("Retrying...")
                await asyncio.sleep(1)
        else:
            print("Failed")


async def main(lesson_ids):
    async with aiohttp.ClientSession() as session:
        # group them into 50, to avoid too many requests:
        lesson_ids_grouped = [lesson_ids[i:i + GROUP_SIZE]
                              for i in range(0, len(lesson_ids), GROUP_SIZE)]
        # run them in parallel:
        semaphores = asyncio.Semaphore(10)
        progress = tqdm.tqdm(total=len(lesson_ids))
        tasks = [update_lessons(lesson_ids_group, semaphores, progress, session)
                 for lesson_ids_group in lesson_ids_grouped]
        with progress:
            await asyncio.gather(*tasks)


class Command(BaseCommand):
    help = "Fetch lecture info from USTC JW"

    def add_arguments(self, parser):
        return super().add_arguments(parser)

    def handle(self, *args, **options):
        # lesson_ids = list(Lesson.objects.all().values_list("jw_id", flat=True))
        lesson_ids = list(Lesson.objects.all()
                          #   .filter(semester_id="65")
                          .values_list("jw_id", flat=True))
        print(len(lesson_ids))

        global cookie, headers
        cookie = input(
            "Login to https://jw.ustc.edu.cn/ and copy the cookies here:")
        if not cookie:
            raise CommandError("No cookies provided")

        headers = {
            "cookie": cookie,
            "accept": "application/json, text/javascript, */*; q=0.01",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "authority": "jw.ustc.edu.cn",
            "referer": f"https://jw.ustc.edu.cn/ws/schedule-table/datum",
        }

        asyncio.run(main(lesson_ids))
