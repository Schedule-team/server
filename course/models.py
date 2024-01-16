from django.db import models


class Course(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=20)  # 课程编号 MATH001108 (短，多个课程共用)
    name = models.CharField(max_length=20)  # 课程名
    period = models.IntegerField()  # 学时
    credits = models.FloatField()  # 学分

    type_base = models.CharField(max_length=20)  # 课程类别
    type_teaching_method = models.CharField(max_length=20)  # 教学类型
    type_join_type = models.CharField(max_length=20)  # 选课类型
    type_level = models.CharField(max_length=20)  # 课程层次
    open_department = models.CharField(max_length=20)  # 开课单位

    exam_type = models.CharField(max_length=20)  # 考核方式
    grading_type = models.CharField(max_length=20)  # 评分制 (五等级制/百分制/二等级制)

    description = models.CharField(max_length=1000, blank=True, null=True)  # 课程描述
    info = models.CharField(max_length=10000)  # json string for other info

    def __str__(self):
        return f"{self.name} ({self.code})"


class Teacher(models.Model):
    id = models.AutoField(primary_key=True)

    jw_id = models.CharField(unique=True, max_length=20)  # 教务系统 ID, 识别教师用 (重名)

    name = models.CharField(max_length=20)
    email = models.CharField(max_length=100, blank=True, null=True)
    office_location = models.CharField(max_length=100, blank=True, null=True)
    homepage_url = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.email})"


class Semester(models.Model):
    id = models.AutoField(primary_key=True)

    jw_id = models.CharField(unique=True, max_length=20)  # 教务系统 ID

    code = models.CharField(max_length=20)  # 2023FA
    name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"{self.name} ({self.code}) ({self.start_date} - {self.end_date})"


class Location(models.Model):
    id = models.AutoField(primary_key=True)
    campus = models.CharField(max_length=20)
    builiding = models.CharField(max_length=20)
    room = models.CharField(max_length=20)


class Lesson(models.Model):
    class Lecture(models.Model):
        id = models.AutoField(primary_key=True)
        lesson_info = models.ForeignKey("Lesson", on_delete=models.CASCADE)

        teachers = models.ManyToManyField(Teacher)
        start_time = models.DateTimeField()
        end_time = models.DateTimeField()

        location = models.ForeignKey(Location, on_delete=models.CASCADE)

    class Exam(models.Model):
        id = models.AutoField(primary_key=True)
        lesson_info = models.ForeignKey("Lesson", on_delete=models.CASCADE)
        type = models.CharField(max_length=20)  # 考试类型：期中考试/期末考试/补考

        start_time = models.DateTimeField()
        end_time = models.DateTimeField()

        description = models.CharField(max_length=1000)  # 考试描述，例如 开卷/闭卷 注意事项等

        location = models.ForeignKey(Location, on_delete=models.CASCADE)

    id = models.AutoField(primary_key=True)

    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    teachers = models.ManyToManyField(Teacher)

    code = models.CharField(max_length=20)  # MATH001108.01 (长，一个课程一个课号)
    campus = models.CharField(max_length=20)  # 校区
    start_week = models.IntegerField(blank=True, null=True)  # 开始周
    end_week = models.IntegerField(blank=True, null=True)  # 结束周
    schedule_text = models.CharField(
        max_length=100, blank=True, null=True
    )  # 上课时间：1-12 周 5503: 1(8,9,10)

    lectures = models.ManyToManyField(Lecture)
    exams = models.ManyToManyField(Exam)

    homepage_url = models.CharField(max_length=100)  # 课程主页

    def __str__(self):
        return f"{self.course.name} ({self.code})"