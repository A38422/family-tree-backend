from django.urls import path
from .views import ImageUploadView

urlpatterns = [
    path('api/image-upload/', ImageUploadView.as_view(), name='image-upload')
]