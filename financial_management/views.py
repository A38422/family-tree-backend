from django.db import models
from django.db.models import Q

from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError

from family_tree_manager.models import FamilyTree
from family_tree_manager.serializers import FamilyTreeSerializer
from .models import ContributionLevel, Sponsor, Income, ExpenseCategory, Expense
from rest_framework.filters import SearchFilter, OrderingFilter
from .serializers import (
    ContributionLevelSerializer, SponsorSerializer,
    IncomeSerializer, ExpenseCategorySerializer, ExpenseSerializer
)
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from django_filters import rest_framework as filters


class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return False


class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return False


class BasePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'


class ContributionLevelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperUserOrReadOnly]
    queryset = ContributionLevel.objects.all()
    serializer_class = ContributionLevelSerializer
    pagination_class = BasePagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['year', 'amount', 'note']
    ordering_fields = '__all__'

    def list(self, request, *args, **kwargs):
        if 'query_all' in request.query_params:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return super().list(request, *args, **kwargs)


class SponsorFilter(filters.FilterSet):
    # start_date = filters.DateFromToRangeFilter(field_name='start_date')
    start_date_before = filters.DateFilter(field_name='start_date', lookup_expr='gte')
    start_date_after = filters.DateFilter(field_name='start_date', lookup_expr='lte')

    class Meta:
        model = Sponsor
        fields = {
            'start_date': ['range'],
        }


class SponsorViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperUserOrReadOnly]
    queryset = Sponsor.objects.all()
    serializer_class = SponsorSerializer
    pagination_class = BasePagination
    filter_backends = [SearchFilter, OrderingFilter, filters.DjangoFilterBackend]
    search_fields = ['name', 'phone', 'address', 'amount']
    ordering_fields = '__all__'
    filterset_class = SponsorFilter

    def list(self, request, *args, **kwargs):
        if 'query_all' in request.query_params:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return super().list(request, *args, **kwargs)


def validate_unique(contributor_id, member_id):
    # Kiểm tra tính duy nhất của sponsor và member
    if contributor_id and member_id:
        queryset = Income.objects.filter(contributor_id=contributor_id, member_id=member_id)
        if queryset.exists():
            raise ValidationError('Contributor and member must be unique.')


class IncomeFilter(filters.FilterSet):
    # date = filters.DateFromToRangeFilter(field_name='date')
    date_before = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_after = filters.DateFilter(field_name='date', lookup_expr='lte')
    contributor = filters.BooleanFilter(field_name='contributor', method='filter_contributor')
    year = filters.NumberFilter(field_name='contributor__year')

    def filter_contributor(self, queryset, name, value):
        if value is True:
            return queryset.filter(contributor__isnull=False)
        elif value is False:
            return queryset.filter(contributor__isnull=True)
        return queryset

    class Meta:
        model = Income
        fields = {
            'date': ['range'],
            'contributor': ['exact', 'isnull'],
            'contributor__year': ['exact']
        }


class IncomeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperUserOrReadOnly]
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    pagination_class = BasePagination
    filter_backends = [SearchFilter, OrderingFilter, filters.DjangoFilterBackend]
    search_fields = ['date', 'contributor__amount', 'contributor__year', 'sponsor__name',
                     'sponsor__amount', 'member__name']
    ordering_fields = ['id', 'date', 'contributor__amount']  # or'__all__'
    filterset_fields = {
        'contributor': ['isnull'],
    }
    filterset_class = IncomeFilter

    def list(self, request, *args, **kwargs):
        if 'query_all' in request.query_params:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        contributor_id = request.data.pop('contributor', None)
        sponsor_id = request.data.pop('sponsor', None)
        member_id = request.data.pop('member', None)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # Kiểm tra tính duy nhất của sponsor và member
        validate_unique(contributor_id, member_id)

        income = serializer.instance

        if contributor_id:
            contributor = ContributionLevel.objects.get(id=contributor_id)
            income.contributor = contributor

        if sponsor_id:
            sponsor = Sponsor.objects.get(id=sponsor_id)
            income.sponsor = sponsor

        if member_id:
            member = FamilyTree.objects.get(id=member_id)
            income.member = member

        income.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        contributor_id = request.data.pop('contributor', None)
        sponsor_id = request.data.pop('sponsor', None)
        member_id = request.data.pop('member', None)

        if contributor_id:
            contributor = ContributionLevel.objects.get(id=contributor_id)
            instance.contributor = contributor

        if sponsor_id:
            sponsor = Sponsor.objects.get(id=sponsor_id)
            instance.sponsor = sponsor

        if member_id:
            member = FamilyTree.objects.get(id=member_id)
            instance.member = member

        instance.save()

        return Response(serializer.data)


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperUserOrReadOnly]
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    pagination_class = BasePagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'note']
    ordering_fields = '__all__'

    def list(self, request, *args, **kwargs):
        if 'query_all' in request.query_params:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return super().list(request, *args, **kwargs)


class ExpenseFilter(filters.FilterSet):
    # date = filters.DateFromToRangeFilter(field_name='date')
    date_before = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_after = filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Expense
        fields = {
            'date': ['range'],
        }


class ExpenseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperUserOrReadOnly]
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    pagination_class = BasePagination
    filter_backends = [SearchFilter, OrderingFilter, filters.DjangoFilterBackend]
    search_fields = ['category__name', 'amount']
    ordering_fields = '__all__'
    filterset_class = ExpenseFilter

    def list(self, request, *args, **kwargs):
        if 'query_all' in request.query_params:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        category_id = request.data.pop('category', None)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        income = serializer.instance

        if category_id:
            category = ExpenseCategory.objects.get(id=category_id)
            income.category = category

        income.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        category_id = request.data.pop('category', None)

        if category_id:
            category = ExpenseCategory.objects.get(id=category_id)
            instance.category = category

        instance.save()

        return Response(serializer.data)


class UnpaidMemberViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsReadOnly]
    queryset = FamilyTree.objects.all()
    serializer_class = FamilyTreeSerializer
    pagination_class = BasePagination
    search_fields = ['name']

    def list(self, request, *args, **kwargs):
        contribution_level_year = request.query_params.get('contribution_level_year')
        search = request.query_params.get('search', '')
        if contribution_level_year:
            data = []
            query_set = FamilyTree.objects.filter(Q(name__icontains=search))
            for family_tree in query_set:
                if not Income.objects.filter(member_id=family_tree.id, contributor__year=contribution_level_year):
                    data.append(family_tree)

            page = self.paginate_queryset(data)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)
        raise ValidationError("Must have param contribution_level_year")


class ReportViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated, IsSuperUserOrReadOnly]

    def list(self, request, *args, **kwargs):
        type = request.query_params.get('type')
        search = request.query_params.get('search') or ''
        date_before = request.query_params.get('date_before')
        date_after = request.query_params.get('date_after')

        if date_before and date_after:
            expenses = Expense.objects.filter(
                date__range=[date_before,
                             date_after],
                amount__icontains=search) if type == 'chi' or type == 'thu-chi' else Expense.objects.filter(
                id__isnull=True)
            incomes = Income.objects.filter(
                contributor__isnull=False,
                date__range=[date_before, date_after],
                contributor__amount__icontains=search) if type == 'thu' or type == 'thu-chi' else Income.objects.filter(
                id__isnull=True)
            sponsors = Sponsor.objects.filter(
                start_date__range=[date_before,
                                   date_after],
                amount__icontains=search) if type == 'thu' or type == 'thu-chi' else Sponsor.objects.filter(
                id__isnull=True)
        else:
            expenses = Expense.objects.filter(amount__icontains=search) if type == 'chi' or type == 'thu-chi' else Expense.objects.filter(
                id__isnull=True)
            incomes = Income.objects.filter(
                contributor__isnull=False,
                contributor__amount__icontains=search) if type == 'thu' or type == 'thu-chi' else Income.objects.filter(
                id__isnull=True)
            sponsors = Sponsor.objects.filter(amount__icontains=search) if type == 'thu' or type == 'thu-chi' else Sponsor.objects.filter(
                id__isnull=True)

        total_amount_expenses = expenses.aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0
        total_amount_incomes = incomes.aggregate(total_contributor__amount=models.Sum('contributor__amount'))[
                                   'total_contributor__amount'] or 0
        total_amount_sponsors = sponsors.aggregate(total_amount=models.Sum('amount'))['total_amount'] or 0
        total_amount = total_amount_incomes + total_amount_sponsors - total_amount_expenses

        expense_serializer = ExpenseSerializer(expenses, many=True)
        income_serializer = IncomeSerializer(incomes, many=True)
        sponsor_serializer = SponsorSerializer(sponsors, many=True)

        report_data = {
            'expenses': expense_serializer.data,
            'incomes': income_serializer.data,
            'sponsors': sponsor_serializer.data,
            'total_amount': total_amount,
        }

        return Response(report_data)
