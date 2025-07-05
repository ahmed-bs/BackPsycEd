from rest_framework import viewsets, permissions
from .models import Goal, SubObjective
from .serializers import GoalSerializer, SubObjectiveSerializer

class GoalViewSet(viewsets.ModelViewSet):
    serializer_class = GoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Goal.objects.filter(user=self.request.user).prefetch_related('sub_objectives')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)