from django.contrib import admin
from .models import Farm, CropHistory

@admin.register(Farm)
class FarmAdmin(admin.ModelAdmin):
    list_display  = ['name', 'owner', 'state', 'size_hectares', 'soil_type', 'is_active']
    list_filter   = ['soil_type', 'agro_zone', 'is_active', 'state']
    search_fields = ['name', 'owner__username', 'location_name']

@admin.register(CropHistory)
class CropHistoryAdmin(admin.ModelAdmin):
    list_display = ['crop_name', 'farm', 'season', 'planting_date', 'status']
    list_filter  = ['status', 'season', 'crop_name']
