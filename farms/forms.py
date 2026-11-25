from django import forms
from .models import Farm, CropHistory

class FarmForm(forms.ModelForm):
    class Meta:
        model   = Farm
        exclude = ['owner', 'created_at', 'updated_at', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'latitude':    forms.NumberInput(attrs={'step': '0.000001'}),
            'longitude':   forms.NumberInput(attrs={'step': '0.000001'}),
            'soil_ph':     forms.NumberInput(attrs={'step': '0.1', 'min': '3', 'max': '10'}),
        }

class CropHistoryForm(forms.ModelForm):
    class Meta:
        model   = CropHistory
        exclude = ['farm', 'created_at']
        widgets = {
            'planting_date': forms.DateInput(attrs={'type': 'date'}),
            'harvest_date':  forms.DateInput(attrs={'type': 'date'}),
            'notes':         forms.Textarea(attrs={'rows': 2}),
        }
