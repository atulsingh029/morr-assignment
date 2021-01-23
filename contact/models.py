from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(max_length=512, unique=True)

    def __str__(self):
        return self.email


class Contact(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='custom_user')
    email = models.EmailField(max_length=512)
    name = models.CharField(max_length=300)
    address = models.CharField(max_length=512, null=True, blank=True)
    phone1 = models.IntegerField(null=True, blank=True)
    phone2 = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.email