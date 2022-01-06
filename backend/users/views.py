from typing import Optional
import json

from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import SignUpSerializer, LogInSerializer, \
                         UsersListSerializer, ChangePasswordSerializer
from .models import User
from .services import TokenService, UserService


class SignUpView(APIView):
    """View for registration user"""

    def post(self, request) -> Response:
        """
        Registrate user and send email for account activation.
        Return response about success registration or about fail
        """
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            UserService.create_user_and_send_email_for_activation(
                request, **serializer.data)
            json = serializer.data
            json["message"] = "Check your email for activate account."
            del json['password']
            return Response(data=json,
                            status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def get(self, request) -> Response:
        return Response(status=status.HTTP_200_OK)


class AccountActivationView(APIView):
    """View for activate user account"""

    def get(self, request, id: int, token: str) -> Response:
        """
        Activate user and return response
        about success registration or about fail.
        """
        try:
            user = User.objects.get(id=id)
        except:
            data = {"message": "Activation account is faild."}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)

        if TokenService.check_activation_token(token, user):
            UserService.activate_user(user)
            data = {
                "message": "account was activated",
            }
            return Response(data=data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class LogInView(APIView):
    """
    View for authenticate user and return him token
    for further authentication and authorization.
    """

    def post(self, request) -> Response:
        """
        Authenticate user and return response with data
        with contain private token for authentication
        """
        serializer = LogInSerializer(data=request.data)
        if serializer.is_valid():
            user = self.__get_authenticated_user(serializer.data)
            if not user:
                data={"message": "Username or password uncorrect."}
                return Response(data=data,
                                status=status.HTTP_400_BAD_REQUEST)

            if user.is_activated:
                token = TokenService.get_user_auth_token(user)
                data = serializer.data
                data["token"] = token
                return Response(data=data,
                                status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def __get_authenticated_user(self, data: dict) -> Optional[User]:
        """Authenticate user and return him."""
        username = data["username"]
        password = data["password"]
        user = authenticate(username=username, password=password)
        return user


class UsersListView(APIView):
    """View for getting users list."""

    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        """Returns list of users."""
        users_list = self.__get_users_list()
        return Response(data=users_list, status=status.HTTP_200_OK)

    def __get_users_list(self) -> list:
        """Create queryset than serialize it and return users list."""
        queryset = User.objects.all()
        serializer = UsersListSerializer(queryset, many=True)
        return json.loads(json.dumps(serializer.data))


class LogOutView(APIView):
    """View for logs user out."""

    permission_classes = [IsAuthenticated]

    def get(self, request) -> Response:
        """Logs user out."""
        user = request.user
        TokenService.delete_user_auth_token(user)
        return Response(status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """View for change user password."""

    permission_classes = [IsAuthenticated]

    def post(self, request) -> Response:
        """Change user password and delete his authentication token."""
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            UserService.change_user_password(user, serializer.data["new_password"])
            TokenService.delete_user_auth_token(user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
