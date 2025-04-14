from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

class EmailOrUsernameModelBackend(ModelBackend):
    """
    Authenticate using either email or username.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Check if input is email
            if '@' in username:
                user = UserModel.objects.get(email__iexact=username)
            else:
                user = UserModel.objects.get(username__iexact=username)
            
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None
        except Exception:
            return None
