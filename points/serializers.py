from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.gis.geos import Point as GeoPoint
# from django.contrib.auth.models import User
from .models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import Point, Message, AuthToken


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, min_length=8, write_only=True, style={'input_type': 'password'})

    def validate_email(self, value):
        try:
            validate_email(value)
        except ValidationError:
            raise serializers.ValidationError('Invalid email')

        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('Email already exists')

        return value.lower()

    def create(self, validated_data):
        return User.objects.create_user(email=validated_data['email'], password=validated_data['password'])


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True, style={'input_type': 'password'})

    def validate(self, data):
        email = data.pop('email', '').lower()
        password = data.get('password', '')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': "User not found"})

        if not user.check_password(password):
            raise serializers.ValidationError({'password': 'Wrong password'})

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError('Authentication failed')

        data['user'] = user
        return data


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthToken
        fields = ['key', 'user']


class PointSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True, required=True)
    longitude = serializers.FloatField(write_only=True, required=True)

    class Meta:
        model = Point
        fields = ['id', 'name', 'description', 'latitude', 'longitude', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        location = GeoPoint(longitude, latitude, srid=4326)
        user = self.context['request'].user

        if 'user' in validated_data:
            validated_data.pop('user')

        point = Point.objects.create(user=user, location=location, **validated_data)

        return point

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['latitude'] = instance.latitude
        representation['longitude'] = instance.longitude
        return representation


class MessageSerializer(serializers.ModelSerializer):
    point_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Message
        fields = ['id', 'point_id', 'text', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        point_id = validated_data.pop('point_id')
        user = self.context['request'].user

        try:
            point = Point.objects.get(id=point_id, user=user)
        except Point.DoesNotExist:
            raise serializers.ValidationError({'point_id': "Point not found"})

        message = Message.objects.create(point=point, user=user, **validated_data)

        return message

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['point'] = {
            'id': instance.point.id,
            'name': instance.point.name,
            'latitude': instance.point.latitude,
            'longitude': instance.point.longitude,
        }
        return representation


class SearchSerializer(serializers.Serializer):
    latitude = serializers.FloatField(required=True, min_value=-90, max_value=90)
    longitude = serializers.FloatField(required=True, min_value=-180, max_value=180)
    radius = serializers.IntegerField(required=True, min_value=0.1, max_value=1000, help_text="Radius in kilometers")