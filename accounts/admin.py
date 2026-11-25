from django.contrib import admin
from .models import FarmerProfile

@admin.register(FarmerProfile)
class FarmerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'state', 'lga', 'phone', 'created_at']
    search_fields = ['user__username', 'user__email', 'state']
    list_filter  = ['state']
