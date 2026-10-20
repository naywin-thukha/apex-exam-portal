from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """SRS User + Role. Passwords are hashed by Django; is_active handles
    activation/deactivation. Accounts are created by an administrator only."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Administrator"
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.role})"