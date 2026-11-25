from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/',    admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('farms/',    include('farms.urls')),
    path('advisory/', include('advisory.urls')),
    path('disease/',  include('disease.urls')),
    path('',          include('reports.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
