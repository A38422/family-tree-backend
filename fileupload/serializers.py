from rest_framework import serializers
from .models import File
import base64


class FileSerializer(serializers.ModelSerializer):
    file_data = serializers.SerializerMethodField()

    class Meta:
        model = File
        fields = ('id', 'file', 'file_data')

    def get_file_data(self, obj):
        with open(obj.file.path, 'rb') as file:
            file_data = base64.b64encode(file.read()).decode('utf-8')
        return file_data
