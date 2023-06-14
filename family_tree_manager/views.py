from rest_framework import viewsets
from rest_framework.views import APIView
from django.db.models import Count

from .models import FamilyTree
from .serializers import FamilyTreeSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS

from django_filters import rest_framework as filters


class FamilyTreeFilter(filters.FilterSet):
    gender = filters.CharFilter(lookup_expr='exact')
    generation = filters.NumberFilter(lookup_expr='exact')
    pids = filters.ModelMultipleChoiceFilter(queryset=FamilyTree.objects.all())
    mid = filters.ModelChoiceFilter(queryset=FamilyTree.objects.all())
    fid = filters.ModelChoiceFilter(queryset=FamilyTree.objects.all())

    class Meta:
        model = FamilyTree
        fields = ['gender', 'generation', 'pids', 'mid', 'fid']


class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        if request.method == 'PUT' or request.method == 'PATCH':
            return request.user == view.get_object().user

        return False


class FamilyTreePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'


class FamilyTreeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperUserOrReadOnly]
    queryset = FamilyTree.objects.all().order_by('id')
    serializer_class = FamilyTreeSerializer
    pagination_class = FamilyTreePagination
    filter_backends = [SearchFilter, OrderingFilter, filters.DjangoFilterBackend]
    filterset_class = FamilyTreeFilter
    # filterset_fields = ['id', 'gender', 'generation']
    search_fields = ['name']
    ordering_fields = '__all__'

    def list(self, request, *args, **kwargs):
        if 'query_all' in request.query_params:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return super().list(request, *args, **kwargs)


class FamilyTreeStatisticsAPIView(APIView):
    def get(self, request, format=None):
        statistics_generations = FamilyTree.objects.values('generation').annotate(member_count=Count('id')).order_by(
            'generation')
        generations = [{'generation': stat['generation'], 'member_count': stat['member_count']} for stat in
                       statistics_generations]

        statistics_educations = FamilyTree.objects.values('education').annotate(member_count=Count('id'))
        educations = [{'education': stat['education'], 'member_count': stat['member_count']} for stat in
                      statistics_educations]

        statistics_genders = FamilyTree.objects.values('gender').annotate(member_count=Count('id'))
        genders = [{'gender': stat['gender'], 'member_count': stat['member_count']} for stat in statistics_genders]

        data = {
            'generations': generations,
            'educations': educations,
            'genders': genders
        }

        return Response(data)
