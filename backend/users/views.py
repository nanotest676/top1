from api.serializers import CustomUserSerializer
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.pagination import PageNumberPagination

User = get_user_model()

class CustomPagination(PageNumberPagination):
    page_size_query_param = "limit"

class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination
