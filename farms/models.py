from django.db import models
from django.contrib.auth.models import User

SOIL_TYPES = [
    ('clay','Clay'),('sandy','Sandy'),('loamy','Loamy'),
    ('silty','Silty'),('peat','Peat'),
]

class Farm(models.Model):
    owner               = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farms')
    name                = models.CharField(max_length=100)
    location_name       = models.CharField(max_length=150)
    state               = models.CharField(max_length=100, default='FCT')
    lga                 = models.CharField(max_length=100, blank=True)
    latitude            = models.FloatField(default=9.0579)
    longitude           = models.FloatField(default=7.4951)
    size_hectares       = models.FloatField(default=1.0)
    soil_type           = models.CharField(max_length=20, choices=SOIL_TYPES, default='loamy')
    agro_zone           = models.CharField(max_length=100, blank=True)
    soil_ph             = models.FloatField(default=6.5)
    nitrogen            = models.FloatField(default=40, help_text='mg/kg')
    phosphorus          = models.FloatField(default=35, help_text='mg/kg')
    potassium           = models.FloatField(default=50, help_text='mg/kg')
    irrigation_available = models.BooleanField(default=False)
    description         = models.TextField(blank=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)
    is_active           = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

class CropHistory(models.Model):
    STAGE_CHOICES = [
        ('planted','Planted'),('growing','Growing'),
        ('harvested','Harvested'),('failed','Failed'),
    ]
    farm           = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='crop_history')
    crop_name      = models.CharField(max_length=80)
    season         = models.CharField(max_length=50)
    planting_date  = models.DateField()
    harvest_date   = models.DateField(null=True, blank=True)
    area_planted   = models.FloatField(default=1.0, help_text='hectares')
    actual_yield   = models.FloatField(null=True, blank=True, help_text='tons/ha')
    fertilizer_used = models.CharField(max_length=150, blank=True)
    status         = models.CharField(max_length=20, choices=STAGE_CHOICES, default='planted')
    notes          = models.TextField(blank=True)
    created_at     = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-planting_date']
