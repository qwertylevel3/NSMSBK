from django.contrib.auth.decorators import user_passes_test

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.models import User



def isSuperuser(user):
    if user.is_authenticated:
        name=user.get_username()
        if User.objects.get(username=name).is_superuser:
            return True
    return False

def super_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None):
    actual_decorator = user_passes_test(
        isSuperuser,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
