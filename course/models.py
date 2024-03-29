from django.db import models
from simple_history.models import HistoricalRecords
from user.models import CustomUser as User


class EditableTextModel(models.Model):
    id = models.AutoField(primary_key=True)

    text = models.TextField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.TextField(blank=True, null=True)
    history = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.text}"

    def update(self, text, last_modified, last_modified_by):
        self.text = text
        self.last_modified = last_modified
        self.last_modified_by = last_modified_by
        self.history = f"""
        {last_modified_by} @ {last_modified} :

        {text}
        ==========
        {self.history}
        """
        self.save()


class Semester(models.Model):
    id = models.AutoField(primary_key=True)
    jw_id = models.TextField(unique=True)  # 教务系统 ID

    code = models.TextField()  # 202301 (学年 + 学期)
    name = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.code}) ({self.start_date} - {self.end_date})"


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    jw_id = models.TextField(unique=True)  # 教务系统 ID

    semesters = models.ManyToManyField(
        Semester,
        related_name="semester_courses",
        blank=True
    )

    # 课程编号 MATH001108 (短，多个课堂共用)
    code = models.TextField(unique=True)
    name = models.TextField(blank=True, null=True)  # 课程名
    period = models.IntegerField(blank=True, null=True)  # 学时
    credits = models.FloatField(blank=True, null=True)  # 学分

    type_base = models.TextField(blank=True, null=True)  # 课程类别
    type_teaching_method = models.TextField(blank=True, null=True)  # 教学类型
    type_join_type = models.TextField(blank=True, null=True)  # 选课类型
    type_level = models.TextField(blank=True, null=True)  # 课程层次
    open_department = models.TextField(blank=True, null=True)  # 开课单位

    exam_type = models.TextField(blank=True, null=True)  # 考核方式
    grading_type = models.TextField(
        blank=True, null=True
    )  # 评分制 (五等级制/百分制/二等级制)

    description = models.TextField(blank=True, null=True)  # 课程描述
    # json string for other info
    info = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Teacher(models.Model):
    id = models.AutoField(primary_key=True)
    jw_id = models.TextField(unique=True)  # 教务系统 ID, 识别教师用 (重名)

    name = models.TextField()
    email = models.TextField(blank=True, null=True)
    office_location = models.TextField(blank=True, null=True)
    homepage_url = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    jw_id = models.TextField(unique=True)  # 教务系统 ID

    campus = models.TextField()
    building = models.TextField()
    room = models.TextField()

    def __str__(self):
        return f"{self.campus} {self.building} {self.room}"


class Lesson(models.Model):
    id = models.AutoField(primary_key=True)
    jw_id = models.TextField(unique=True)  # 教务系统 ID

    semester = models.ForeignKey(
        Semester,
        related_name="semester_lessons",
        on_delete=models.CASCADE
    )
    course = models.ForeignKey(
        Course,
        related_name="course_lessons",
        on_delete=models.CASCADE
    )
    teachers = models.ManyToManyField(
        Teacher,
        related_name="teacher_lessons",
        blank=True
    )

    code = models.TextField()  # MATH001108.01 (长，一个课程一个课号)
    campus = models.TextField()  # 校区
    start_week = models.IntegerField(blank=True, null=True)  # 开始周
    end_week = models.IntegerField(blank=True, null=True)  # 结束周
    schedule_text = models.TextField(
        blank=True, null=True
    )  # 上课时间：1-12 周 5503: 1(8,9,10)

    homepage_url = models.TextField(blank=True, null=True)  # 课程主页

    notice_md_text = models.ForeignKey(
        EditableTextModel,
        on_delete=models.CASCADE,
        related_name="notice",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.course.name} ({self.code})"

    @property
    def teachers_name(self):
        return ", ".join([teacher.name for teacher in self.teachers.all()])


class Lecture(models.Model):
    id = models.AutoField(primary_key=True)
    # jw_id = models.TextField(unique=True)  # 教务系统 ID

    lesson = models.ForeignKey(
        Lesson,
        related_name="lesson_lectures",
        on_delete=models.CASCADE
    )
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, blank=True, null=True
    )

    teachers = models.ManyToManyField(Teacher, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.lesson.course.name} ({self.lesson.code}) {self.start_time} - {self.end_time}"


class Exam(models.Model):
    id = models.AutoField(primary_key=True)
    jw_id = models.TextField(unique=True)  # 教务系统 ID

    lesson = models.ForeignKey(
        Lesson,
        related_name="lesson_exams",
        on_delete=models.CASCADE
    )
    locations = models.ManyToManyField(Location, blank=True)

    type = models.TextField()  # 考试类型：期中考试/期末考试/补考

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    description = models.TextField()  # 考试描述，例如 开卷/闭卷 注意事项等

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.lesson.course.name} ({self.lesson.code}) {self.type} {self.start_time} - {self.end_time}"


class Homework(models.Model):
    id = models.AutoField(primary_key=True)

    lesson = models.ForeignKey(
        Lesson,
        related_name="lesson_homeworks",
        on_delete=models.CASCADE
    )

    description = models.TextField()
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    history = HistoricalRecords()

    def __str__(self):
        return f"{self.lesson.course.name} ({self.lesson.code}) {self.description} {self.deadline}"


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    lessons = models.ManyToManyField(Lesson, blank=True)

    def register_lesson_ids(self, lesson_ids):
        for lesson_id in lesson_ids:
            lesson = Lesson.objects.get(id=lesson_id)
            self.lessons.add(lesson)
        self.save()
