from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from users.serializers import CustomUserSerializer, SubscribeSerializer
from .models import Subscribe
from djoser.views import UserViewSet
from rest_framework.response import Response

User = get_user_model()

class CustomPagination(PageNumberPagination):
    page_size_query_param = "limit"

class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    serializer_class = CustomUserSerializer
    

    @action(
        detail=True,
        permission_classes=[IsAuthenticated,],
        methods=['post', 'delete']

    )
    def subscribe(self, request, **kwargs):
        author_id = self.kwargs.get('id')
        user = request.user
        author = get_object_or_404(User, id=author_id)
        
        if user == author:
            return Response({"error": "Нельзя подписаться на самого себя"}, status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            subscription = Subscribe.objects.filter(user=user, author=author).first()
            if subscription:
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Вы не подписаны на этого пользователя"}, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'POST':
            if Subscribe.objects.filter(user=user, author=author).exists():
                return Response({"error": "Вы уже подписаны на этого пользователя"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = SubscribeSerializer(
                author,
                data=request.data,
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            Subscribe.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        permission_classes=[IsAuthenticated,],
        detail=False,
    )
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribing__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages,
            context={'request': request},
            many=True,
        )
        return self.get_paginated_response(serializer.data)
