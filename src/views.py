from rest_framework import status
from rest_framework.decorators import api_view, action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from family_tree_manager.models import FamilyTree
from family_tree_manager.serializers import FamilyTreeSerializer
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from src.serializers import UserSerializer, ChangePasswordSerializer
from django_filters import rest_framework as filters


@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    # Kiểm tra xác thực người dùng
    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)

        family_tree = FamilyTree.objects.filter(user_id=user.id).first()

        if family_tree:
            serializer = FamilyTreeSerializer(family_tree)
            family_tree_json = serializer.data

            if family_tree.mid:
                family_tree_json['mid'] = {
                    'id': family_tree.mid.id,
                    'name': family_tree.mid.name
                }

            if family_tree.fid:
                family_tree_json['fid'] = {
                    'id': family_tree.fid.id,
                    'name': family_tree.fid.name
                }

            if family_tree.pids.count() > 0:
                family_tree_json['pids'] = [{
                    'id': family_tree.pids.all()[0].id,
                    'name': family_tree.pids.all()[0].name
                }]

            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'access_exp': refresh.access_token.payload['exp'],
                    'user': family_tree_json
                })
        else:
            return Response(
                {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'access_exp': refresh.access_token.payload['exp'],
                    'user': {
                        'name': 'Superuser',
                        'is_admin': True,
                        'is_superuser': True,
                    }
                })
    else:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def logout_view(request):
    # Đăng xuất
    refresh_token = request.data.get('refresh_token')
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logged out successfully'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class IsSuperUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated

        return False


class BasePagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'


class UserFilter(filters.FilterSet):
    date_joined_before = filters.DateFilter(field_name='date_joined', lookup_expr='gte')
    date_joined_after = filters.DateFilter(field_name='date_joined', lookup_expr='lte')

    class Meta:
        model = User
        fields = {
            'date_joined': ['range'],
            'is_superuser': ['exact'],
            'is_active': ['exact'],
        }


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperUserOrReadOnly]
    queryset = User.objects.all().order_by('-id')
    serializer_class = UserSerializer
    pagination_class = BasePagination
    filter_backends = [SearchFilter, OrderingFilter, filters.DjangoFilterBackend]
    filterset_class = UserFilter
    search_fields = ['username']
    ordering_fields = '__all__'

    def list(self, request, *args, **kwargs):
        if 'query_all' in request.query_params:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        else:
            return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        is_admin = request.data.get('is_admin', False)
        member_id = request.data.get('member', None)

        if username and password and member_id:
            try:
                check_user = User.objects.get(username=username)
                raise ValidationError('Tài khoản đã tồn tại.')
            except User.DoesNotExist:
                try:
                    member = FamilyTree.objects.get(id=member_id)

                    validate_password(password)

                    user = None
                    if is_admin:
                        user = User.objects.create_superuser(username=username, password=password)
                    else:
                        user = User.objects.create_user(username=username, password=password)
                    user.save()

                    member.user = user
                    member.is_admin = is_admin
                    member.save()

                    headers = self.get_success_headers(UserSerializer(user).data)
                    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED, headers=headers)
                except Exception as e:
                    error_message = 'invalid'
                    if e and e.messages:
                        error_message = ', '.join(e.messages)
                    raise ValidationError(error_message)

        raise ValidationError()

    def partial_update(self, request, *args, **kwargs):
        password = request.data.get('password', None)
        is_admin = request.data.get('is_admin', None)
        is_active = request.data.get('is_active', None)

        user = self.get_object()

        if is_admin is not None:
            user.is_superuser = is_admin

            try:
                member = FamilyTree.objects.get(user_id=user.id)
                member.is_admin = is_admin
                member.save()
            except Exception as e:
                error_message = 'invalid'
                if e and e.messages:
                    error_message = ', '.join(e.messages)
                raise ValidationError(error_message)

        if is_active is not None:
            user.is_active = is_active

        if password:
            try:
                validate_password(password)
                user.set_password(password)
            except Exception as e:
                error_message = 'invalid'
                if e and e.messages:
                    error_message = ', '.join(e.messages)
                raise ValidationError(error_message)

        user.save()
        return Response(UserSerializer(user).data)

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        member = FamilyTree.objects.get(user_id=user.id)
        member.user = None
        member.user_id = None
        member.save()

        self.perform_destroy(user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def change_password(self, request, *args, **kwargs):
        password = request.data.get('new_password', None)

        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            validate_password(password)
        except Exception as e:
            error_message = 'invalid'
            if e and e.messages:
                error_message = ', '.join(e.messages)
            raise ValidationError(error_message)

        if not user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': ['Incorrect password.']}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully.'})
