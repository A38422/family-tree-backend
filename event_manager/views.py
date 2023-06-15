from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters import rest_framework as filters

from family_tree_manager.models import FamilyTree
from .models import Event
from .serializers import EventSerializer


class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        if request.method == 'PUT' or request.method == 'PATCH':
            return request.user == view.get_object().user

        return False


class BasePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'


class EventFilter(filters.FilterSet):
    date_before = filters.DateFilter(field_name='date', lookup_expr='gte')
    date_after = filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = Event
        fields = {
            'date': ['range'],
        }


class EventViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperUserOrReadOnly]
    queryset = Event.objects.all().order_by('-id')
    serializer_class = EventSerializer
    pagination_class = BasePagination
    filter_backends = [SearchFilter, OrderingFilter, filters.DjangoFilterBackend]
    filterset_class = EventFilter
    search_fields = ['name', 'location', 'description']
    ordering_fields = '__all__'

    def list(self, request, *args, **kwargs):
        if 'query_all' in request.query_params and request.user.is_superuser:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        if request.user.is_superuser:
            return super().list(request, *args, **kwargs)

        family_tree_id = FamilyTree.objects.filter(user_id=request.user.id).first().id
        queryset = Event.objects.filter(attendees__id=family_tree_id)

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
