from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth.models import User


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

    # Address fields
    street_address = models.CharField(max_length=255, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"



@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()