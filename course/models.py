from django.db import models


class EditableTextModel(models.Model):
    id = models.AutoField(primary_key=True)

    text = models.TextField(blank=True, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_by = models.TextField(blank=True, null=True)
    history = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.text}"

    def update(self, text, last_modifed, last_modified_by):
        self.text = text
        self.last_modified = last_modifed
        self.last_modified_by = last_modified_by
        self.history = f"""
        {last_modified_by} @ {last_modifed} : 
        
        {text}
        ==========
        {self.history}
        """
        self.save()


class Course(models.Model):
    id = models.AutoField(primary_key=True)

    jw_id = models.TextField(unique=True)  # 教务系统 ID

    # 课程编号 MATH001108 (短，多个课程共用)
    code = models.TextField(unique=True)
    name = models.TextField()  # 课程名
    period = models.IntegerField()  # 学时
    credits = models.FloatField()  # 学分

    type_base = models.TextField()  # 课程类别
    type_teaching_method = models.TextField()  # 教学类型
    type_join_type = models.TextField()  # 选课类型
    type_level = models.TextField()  # 课程层次
    open_department = models.TextField()  # 开课单位

    exam_type = models.TextField()  # 考核方式
    grading_type = models.TextField()  # 评分制 (五等级制/百分制/二等级制)

    description = models.TextField(blank=True, null=True)  # 课程描述
    info = models.TextField()  # json string for other info

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


class Semester(models.Model):
    id = models.AutoField(primary_key=True)

    jw_id = models.TextField(unique=True)  # 教务系统 ID

    code = models.TextField()  # 202301 (学年 + 学期)
    name = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.code}) ({self.start_date} - {self.end_date})"


class Location(models.Model):
    id = models.AutoField(primary_key=True)

    jw_id = models.TextField(unique=True)  # 教务系统 ID

    campus = models.TextField()
    building = models.TextField()
    room = models.TextField()

    def __str__(self):
        return f"{self.campus} {self.building} {self.room}"


class Lesson(models.Model):
    class Lecture(models.Model):
        id = models.AutoField(primary_key=True)

        # jw_id = models.TextField(unique=True)  # 教务系统 ID

        lesson_info = models.ForeignKey("Lesson", on_delete=models.CASCADE)

        teachers = models.ManyToManyField(Teacher, blank=True)
        start_time = models.DateTimeField()
        end_time = models.DateTimeField()

        location = models.ForeignKey(
            Location, on_delete=models.CASCADE, blank=True, null=True
        )

        def __str__(self):
            return f"{self.lesson_info.course.name} ({self.lesson_info.code}) {self.start_time} - {self.end_time}"

    class Exam(models.Model):
        id = models.AutoField(primary_key=True)

        jw_id = models.TextField(unique=True)  # 教务系统 ID

        lesson_info = models.ForeignKey("Lesson", on_delete=models.CASCADE)
        type = models.TextField()  # 考试类型：期中考试/期末考试/补考

        start_time = models.DateTimeField()
        end_time = models.DateTimeField()

        description = models.TextField()  # 考试描述，例如 开卷/闭卷 注意事项等

        # location = models.ForeignKey(Location, on_delete=models.CASCADE)
        locations = models.ManyToManyField(Location, blank=True)

        def __str__(self):
            return f"{self.lesson_info.course.name} ({self.lesson_info.code}) {self.type} {self.start_time} - {self.end_time}"

    id = models.AutoField(primary_key=True)

    jw_id = models.TextField(unique=True)  # 教务系统 ID

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teachers = models.ManyToManyField(Teacher, blank=True)

    code = models.TextField()  # MATH001108.01 (长，一个课程一个课号)
    campus = models.TextField()  # 校区
    start_week = models.IntegerField(blank=True, null=True)  # 开始周
    end_week = models.IntegerField(blank=True, null=True)  # 结束周
    schedule_text = models.TextField(
        blank=True, null=True
    )  # 上课时间：1-12 周 5503: 1(8,9,10)

    lectures = models.ManyToManyField(Lecture, blank=True)
    exams = models.ManyToManyField(Exam, blank=True)

    homepage_url = models.TextField(blank=True, null=True)  # 课程主页

    # notice_md_text = models.TextField(
    #     blank=True, null=True
    # )  # 课程公告 markdown 文本
    # homework_md_text = models.TextField(
    #     blank=True, null=True
    # )  # 课程作业 markdown 文本
    notice_md_text = models.ForeignKey(
        EditableTextModel,
        on_delete=models.CASCADE,
        related_name="notice",
        blank=True,
        null=True,
    )
    homework_md_text = models.ForeignKey(
        EditableTextModel,
        on_delete=models.CASCADE,
        related_name="homework",
        blank=True,
        null=True,
    )

    def __str__(self):
        return f"{self.course.name} ({self.code})"

    @property
    def teachers_name(self):
        return ", ".join([teacher.name for teacher in self.teachers.all()])
