from rest_framework.permissions import IsAuthenticated


class UsersViewSet():
    permission_classes = (IsAuthenticated,)
