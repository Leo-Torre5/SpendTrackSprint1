import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (1, 'Regular'),
        (2, 'Staff')
    )
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1)
    email = models.EmailField(unique=True)  # Enforce unique emails
    first_name = models.CharField(max_length=30, blank=False)
    last_name = models.CharField(max_length=150, blank=False)

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        default='profiles/default.png'
    )
    phone_number = models.CharField(max_length=20, blank=True)
    street_address = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def delete_old_profile_picture(self):
        if self.profile_picture and hasattr(self.profile_picture, 'name'):
            if self.profile_picture.name != 'profiles/default.png':
                if os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.profile_picture.name)):
                    os.remove(os.path.join(settings.MEDIA_ROOT, self.profile_picture.name))

    def clean(self):
        if self.profile_picture:
            # Validate file type and size
            allowed_types = ['image/jpeg', 'image/png', 'image/gif']
            max_size = 5 * 1024 * 1024  # 5MB

            if self.profile_picture.file.size > max_size:
                raise ValidationError('File size must be under 5MB')

            if hasattr(self.profile_picture.file, 'content_type') and \
                    self.profile_picture.file.content_type not in allowed_types:
                raise ValidationError('Invalid file type')


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()