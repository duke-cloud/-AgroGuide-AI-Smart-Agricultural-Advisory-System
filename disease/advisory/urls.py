from django.urls import path
from . import views

urlpatterns = [
    path('crop/<int:farm_id>/',        views.crop_advisory,        name='crop_advisory'),
    path('fertilizer/<int:farm_id>/',  views.fertilizer_advisory,  name='fertilizer_advisory'),
    path('yield/<int:farm_id>/',       views.yield_prediction,     name='yield_prediction'),
    path('pest/<int:farm_id>/',        views.pest_advisory,        name='pest_advisory'),
    path('weather/<int:farm_id>/',     views.weather_advisory_view,name='weather_advisory'),
    path('chat/<int:farm_id>/',        views.chat_assistant,       name='chat_assistant'),
    path('chat/<int:farm_id>/api/',    views.chat_api,             name='chat_api'),
]
