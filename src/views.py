from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from family_tree_manager.models import FamilyTree
from family_tree_manager.serializers import FamilyTreeSerializer


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
