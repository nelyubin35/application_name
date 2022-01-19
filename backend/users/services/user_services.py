from .email_services import EmailService
from users.models import User


class UserService:
    """Class witch contain all logic belongs to user"""

    @staticmethod
    def create_user_and_send_email_for_activation(request,
                                                  **data: dict) -> User:
        """
        Creates user and send him email with
        link for activation his account.
        """
        user = User.objects.create_user(**data)
        EmailService.send_email_for_activate_account(request, user)
        return user

    @staticmethod
    def activate_user(user: User) -> User:
        """Activates user account."""
        user.is_activated = True
        user.save()
        return user

    @staticmethod
    def change_user_password(user: User, password: str) -> User:
        """Changes user password."""
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def update_user_data(user: User, data: dict) -> User:
        """Update user data."""
        user.first_name = data['first_name']
        user.surname = data['surname']
        user.username = data['username']
        user.slug = user.username
        user.age = data['age']
        user.gender = data['gender']
        user.training_experience = data['training_experience']
        user.trains_now = data['trains_now']
        user.save()
        return user
