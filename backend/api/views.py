from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from users.models import Follow
from recipes.models import Favorite, Recipe, Tag, Ingredient, RecipeIngredient
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    UserCreateSerializer, UserDetailSerializer, IngredientSerializer, UserSerializer,
    RecipeWriteSerializer, RecipeReadSerializer, SubscriptionSerializer, TagSerializer, SetPasswordSerializer
)

User = get_user_model()


class UserViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserDetailSerializer

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        print ("subscriptions user view_set")
        subscriptions = User.objects.filter(following__follower=request.user)
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(subscriptions, many=True, context={'request': request})
        return Response(serializer.data)

    @action(methods=['post', 'delete'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, pk=None):
        print ("subscribe user view_set")
        user = request.user
        author = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            if author == user:
                return Response({'error': 'You cannot subscribe to yourself.'}, status=status.HTTP_400_BAD_REQUEST)
            if Follow.objects.filter(follower=user, following=author).exists():
                return Response({'error': 'Already subscribed.'}, status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(follower=user, following=author)
            serializer = SubscriptionSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = Follow.objects.filter(follower=user, following=author)
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': 'Subscription does not exist.'}, status=status.HTTP_400_BAD_REQUEST)


class UserMe(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SelfUserView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserDetailSerializer(request.user, context={'request': request})
        return Response(serializer.data)


class SetPasswordView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        print ("post SetPasswordView")
        serializer = SetPasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeWriteSerializer
        return RecipeReadSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['post', 'delete'], detail=True, permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        return self._manage_favorite(Favorite, request, pk)

    def _manage_favorite(self, model, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        instance = model.objects.filter(user=user, recipe=recipe)
        if request.method == 'POST':
            if instance.exists():
                return Response({'error': f'This recipe is already in your {model.name}.'}, status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=user, recipe=recipe)
            return Response(status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if instance.exists():
                instance.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'error': f'This recipe is not in your {model.name}.'}, status=status.HTTP_400_BAD_REQUEST)
