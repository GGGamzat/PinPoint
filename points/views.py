from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Point, Message
from .serializers import PointSerializer, MessageSerializer, SearchSerializer


class PointViewSet(viewsets.ModelViewSet):
    serializer_class = PointSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Point.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'])
    def search(self, request):
        serializer = SearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        search_point = Point(x=data['longitude'], y=data['latitude'], srid=4326)

        points = Point.objects.filter(
            location__distance_lte=(search_point, D(km=data['radius']))
        ).annotate(
            distance=Distance('location', search_point)
        ).order_by('distance')

        result_serializer = PointSerializer(points, many=True)

        return Response({
            'count': points.count(),
            'center': {
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'radius_km': data['radius'],
            },
            'points': result_serializer.data,
        })


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user_points = Point.objects.filter(user=self.request.user)
        return Message.objects.filter(point__in=user_points)

    @action(detail=False, methods=['get'])
    def search(self, request):
        serializer = SearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        search_point = Point(x=data['longitude'], y=data['latitude'], srid=4326)

        messages = Message.objects.filter(
            point__location__distance_lte=(search_point, D(km=data['radius']))
        ).annocate(
            distance=Distance('point__location', search_point)
        ).select_related('point', 'user').order_by('-created_at')

        result_serializer = MessageSerializer(messages, many=True)

        return Response({
            'count': messages.count(),
            'center': {
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'radius_km': data['radius'],
            },
            'messages': result_serializer.data,
        })