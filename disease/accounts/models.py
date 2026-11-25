from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class FarmerProfile(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('ha', 'Hausa'),
        ('yo', 'Yoruba'),
        ('ig', 'Igbo'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True, null=True)
    state = models.CharField(max_length=100, default='Abuja')
    lga = models.CharField(max_length=100, blank=True, null=True)
    village = models.CharField(max_length=150, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    preferred_language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='en')
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} — {self.state}"

    class Meta:
        verbose_name = 'Farmer Profile'


@receiver(post_save, sender=User)
def create_or_update_profile(sender, instance, created, **kwargs):
    if created:
        FarmerProfile.objects.create(user=instance)
    else:
        instance.profile.save()
