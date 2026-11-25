from django.db import models
from django.contrib.auth.models import User
from farms.models import Farm

ADVISORY_TYPES = [
    ('crop','Crop Recommendation'),
    ('fertilizer','Fertilizer Recommendation'),
    ('yield','Yield Prediction'),
    ('pest','Pest & Disease Risk'),
    ('planting','Planting Window'),
    ('weather','Weather Advisory'),
]

class AdvisoryRequest(models.Model):
    farmer        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='advisories')
    farm          = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='advisories')
    advisory_type = models.CharField(max_length=20, choices=ADVISORY_TYPES)
    input_data    = models.JSONField(default=dict)
    result_data   = models.JSONField(default=dict)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.advisory_type} | {self.farm.name} | {self.created_at:%Y-%m-%d}"

class ChatMessage(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    role       = models.CharField(max_length=10)   # 'user' or 'assistant'
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
