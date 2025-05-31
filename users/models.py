from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


# Create your models here.

class CustomUser(AbstractUser):
    # Роли пользователей
    STUDENT = 1
    TEACHER = 2
    ROLE_CHOICES = (
        (STUDENT, 'Ученик'),
        (TEACHER, 'Преподаватель'),
    )
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=STUDENT)
    bio = models.TextField(blank=True, null=True)  # Описание профиля
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)  # Фото профиля
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text="The groups this user belongs to",
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text="Specific permissions for this user",
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    class Meta:
        swappable = "AUTH_USER_MODEL"

    def __str__(self):
        return self.username

