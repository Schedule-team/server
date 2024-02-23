from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import *

admin.site.register(Course)
admin.site.register(Teacher)
admin.site.register(Semester)
admin.site.register(Location)
admin.site.register(Lecture, SimpleHistoryAdmin)
admin.site.register(Exam, SimpleHistoryAdmin)
admin.site.register(Lesson, SimpleHistoryAdmin)
admin.site.register(Homework)
admin.site.register(EditableTextModel)
