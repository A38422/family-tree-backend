from rest_framework.serializers import ModelSerializer
from .models import FamilyTree


class FamilyTreeSerializer(ModelSerializer):
    class Meta:
        model = FamilyTree
        # fields = ["id", "mid", "fid", "pids", "gender", "name", "img", "bdate", "ddate", "email",
        #           "phone", "address", "family_info", "generation", "is_admin"]
        fields = '__all__'
