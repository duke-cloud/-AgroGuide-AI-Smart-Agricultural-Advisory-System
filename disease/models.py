from django.db import models
from django.contrib.auth.models import User
from farms.models import Farm

class DiseaseReport(models.Model):
    farmer      = models.ForeignKey(User, on_delete=models.CASCADE)
    farm        = models.ForeignKey(Farm, on_delete=models.CASCADE)
    crop        = models.CharField(max_length=80)
    symptoms    = models.TextField()
    image       = models.ImageField(upload_to='disease_images/', null=True, blank=True)
    diagnosis   = models.CharField(max_length=200, blank=True)
    severity    = models.CharField(max_length=20, blank=True)
    treatment   = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
