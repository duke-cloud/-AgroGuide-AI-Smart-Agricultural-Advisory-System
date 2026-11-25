from django.urls import path
from . import views

urlpatterns = [
    path('',                    views.farm_list,   name='farm_list'),
    path('add/',                views.farm_add,    name='farm_add'),
    path('<int:pk>/',           views.farm_detail, name='farm_detail'),
    path('<int:pk>/edit/',      views.farm_edit,   name='farm_edit'),
    path('<int:pk>/delete/',    views.farm_delete, name='farm_delete'),
]
