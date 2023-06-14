from rest_framework import generics
from .models import Image
from .serializers import ImageSerializer


class ImageUploadView(generics.CreateAPIView):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer
