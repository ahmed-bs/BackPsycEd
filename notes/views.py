from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Note
from .serializers import NoteSerializer
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class NoteViewSet(viewsets.ModelViewSet):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Note.objects.none()

        queryset = Note.objects.all()

        search_query = self.request.query_params.get('search', None)
        if search_query is not None:
            queryset = queryset.filter(content__icontains=search_query)

        important_filter = self.request.query_params.get('important', None)
        if important_filter is not None:
            if important_filter.lower() == 'true':
                queryset = queryset.filter(is_important=True)
            elif important_filter.lower() == 'false':
                queryset = queryset.filter(is_important=False)

        start_date_str = self.request.query_params.get('start_date', None)
        end_date_str = self.request.query_params.get('end_date', None)

        if start_date_str:
            try:
                start_date = datetime.datetime.strptime(start_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start_date)
            except ValueError:
                pass

        if end_date_str:
            try:
                end_date = datetime.datetime.strptime(end_date_str, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end_date)
            except ValueError:
                pass

        author_username = self.request.query_params.get('author_username', None)
        if author_username:
            try:
                author_user = User.objects.get(username__iexact=author_username)
                queryset = queryset.filter(user=author_user)
            except User.DoesNotExist:
                queryset = queryset.none()

        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)