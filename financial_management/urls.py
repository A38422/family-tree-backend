from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ContributionLevelViewSet, SponsorViewSet,
    IncomeViewSet, ExpenseCategoryViewSet, ExpenseViewSet, ReportViewSet
)

router = DefaultRouter()
router.register(r'contribution-levels', ContributionLevelViewSet)
router.register(r'sponsors', SponsorViewSet)
router.register(r'incomes', IncomeViewSet)
router.register(r'expense-categories', ExpenseCategoryViewSet)
router.register(r'expenses', ExpenseViewSet)
router.register(r'report-ie', ReportViewSet, basename='report-ie')

urlpatterns = [
    path('api/', include(router.urls))
]
