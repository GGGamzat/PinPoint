from rest_framework import serializers
from django.contrib.gis.geos import Point
from django.contrib.auth.models import User
from .models import Point, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PointSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    latitude = serializers.FloatField(write_only=True, required=True)
    longitude = serializers.FloatField(write_only=True, required=True)

    class Meta:
        model = Point
        fields = ['id', 'user', 'name', 'description', 'latitude', 'longitude', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        location = Point(longitude, latitude, srid=4326)
        user = self.context['request'].user
        point = Point.objects.create(user=user, location=location, **validated_data)

        return point

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['latitude'] = representation['latitude']
        representation['longitude'] = representation['longitude']
        return representation


class MessageSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    point_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Message
        fields = ['id', 'user', 'point_id', 'text', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def create(self, validated_data):
        point_id = validated_data.pop('point_id')
        user = self.context['request'].user

        try:
            point = Point.objects.get(id=point_id)
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