from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

# Create your models here.
CustomUser = get_user_model()  # Получаем актуальную модель пользователя


class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название курса")
    description = models.TextField(verbose_name="Описание курса")
    teacher = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        limit_choices_to={'role': get_user_model().TEACHER},
        related_name="courses",
        verbose_name="Преподаватель"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_published = models.BooleanField(default=False, verbose_name="Опубликован")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons",
                               verbose_name="Курс")  # Курс, к которому принадлежит урок
    title = models.CharField(max_length=200, verbose_name="Название урока")
    content = models.TextField(verbose_name="Содержание урока")  # Текст урока
    order = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Порядковый номер")
    file = models.FileField(upload_to='lesson_files/', blank=True, null=True, verbose_name="Файл для скачивания")

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['order']  # Сортировка по порядку
        unique_together = ['course', 'order']

    def __str__(self):
        return (f"{self.course.title} - {self.title}")


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="quizzes",
                               verbose_name="Урок")  # Тест привязан к уроку
    title = models.CharField(max_length=200, verbose_name="Название теста")
    description = models.TextField(blank=True, verbose_name="Описание теста")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Тест"
        verbose_name_plural = "Тесты"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Тест: {self.title}({self.lesson})"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions',
                             verbose_name="Тест")  # Вопрос принадлежит тесту
    text = models.TextField(default="Вопрос по умолчанию", verbose_name="Текст вопроса")
    correct_answer = models.CharField(max_length=200, verbose_name="Правильный ответ")
    order = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Порядок вопросов"
    )

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['order']
        unique_together = ['quiz', 'order']

    def __str__(self):
        return f"Вопрос {self.order}: {self.text[:50]}..."


class UserProgress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="progress", verbose_name="Студент")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress",
                               verbose_name="Урок")  # Пройденный урок
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата завершения")
    score = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)],
                                        verbose_name="Результат (%)") 

    class Meta:
        verbose_name = "Прогресс студента"
        verbose_name_plural = "Прогресс студентов"
        unique_together = ['user', 'lesson']
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user} - {self.lesson} ({self.score}%)"


class Enrollment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="enrollments", verbose_name="Студент")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments", verbose_name="Курс")
    enrolled_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата записи")

    class Meta:
        verbose_name = "Запись на курс"
        verbose_name_plural = "Записи на курсы"
        unique_together = ('user', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.username} - {self.course.title}"

