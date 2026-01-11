import binascii
import os
from asyncio import exceptions
from datetime import timedelta
from django.utils import timezone
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from .models import AuthToken


def generate_token():
    return binascii.hexlify(os.urandom(20)).decode()


def create_token(user, expiry_days=30):
    AuthToken.objects.filter(user=user).delete()

    token_key = generate_token()
    expires = timezone.now() + timedelta(days=expiry_days)

    token = AuthToken.objects.create(user=user, key=token_key, expires=expires)
    return token


class TokenAuthentication(BaseAuthentication):
    keyword = 'Token'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) != 2:
            raise exceptions.AuthenticationFailed('Invalid token header')

        try:
            token_day = auth[1].decode()
        except UnicodeError:
            raise exceptions.AuthenticationFailed('Invalid token')

        return self.authenticate_credentials(token_day)

    def authenticate_credentials(self, key):
        try:
            token = AuthToken.objects.select_related('user').get(key=key)
        except AuthToken.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token')

        if token.is_expired():
            token.delete()
            raise exceptions.AuthenticationFailed('Token expired')

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed('User inactive')

        return (token.user, token)

    def authenticate_header(self, request):
        return self.keyword