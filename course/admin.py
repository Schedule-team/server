from django.contrib import admin

from .models import *

admin.site.register(Course)
admin.site.register(Teacher)
admin.site.register(Semester)
admin.site.register(Location)
admin.site.register(Lecture)
admin.site.register(Exam)
admin.site.register(Lesson)
admin.site.register(Homework)
admin.site.register(EditableTextModel)
