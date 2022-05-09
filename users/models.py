from django.db import models

from django.dispatch import receiver 
from rest_framework.authtoken.models import Token 
from django.db.models.signals import post_save

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
                                        PermissionsMixin
class UserManager(BaseUserManager):
    
    def create_user(self, name, password=None, **extra_fields):
        if not name:
            raise ValueError("Users must have a name")

        user = self.model(name=name **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, name, password):
        user = self.model(name=name)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, unique=True, null=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'name'
    objects = UserManager()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)