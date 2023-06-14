from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('family-trees', views.FamilyTreeViewSet, basename='family_tree')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/family-tree-statistics/', views.FamilyTreeStatisticsAPIView.as_view(), name='family_tree_statistics'),
]