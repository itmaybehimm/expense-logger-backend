from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

User._meta.get_field('email')._unique = True


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile")
    otp = models.CharField(max_length=64, null=True, default=None)
    verified = models.BooleanField(default=False)
    otp_created_on = models.DateTimeField(null=True, default=None)
    password_reset = models.BooleanField(default=False)
    dob = models.DateField(null=True)
    profile_pic = models.ImageField(null=True, upload_to='profile_pics/')

    def __str__(self):
        return self.user.username


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.user_profile.save()
