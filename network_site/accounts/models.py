from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, username, display_name=None, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not display_name:
            display_name = username

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            display_name = display_name
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, display_name, password):
        user = self.create_user(
            email,
            username,
            display_name,
            password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user
