"""src URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'user', views.UserViewSet)

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('', include('family_tree_manager.urls')),
                  path('', include('financial_management.urls')),
                  path('', include('event_manager.urls')),
                  path('', include('fileupload.urls')),
                  path('', include('image_upload.urls')),
                  path('api/login/', views.login_view, name='login'),
                  path('api/logout/', views.logout_view, name='logout'),
                  path('api/', include(router.urls)),
                  path('api/user/change-password/<int:pk>/', views.UserViewSet.as_view({'post': 'change_password'}),
                       name='user-change-password'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
