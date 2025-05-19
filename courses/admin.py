from django.contrib import admin
from .models import Course, Lesson, Quiz, Question, UserProgress


# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'created_at')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')


admin.site.register([Quiz, Question, UserProgress])
