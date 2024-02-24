from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, blank=False)
    username = models.CharField(max_length=20, unique=True, blank=False)

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
