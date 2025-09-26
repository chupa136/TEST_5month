from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError


class RegisterValidateSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate_username(self, username):
        try: 
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        raise ValidationError('User with this username already exists')


class AuthValidateSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()