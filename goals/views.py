# goals/views.py
from rest_framework import viewsets
from .models import Goal
from .serializers import GoalSerializer
from rest_framework.response import Response
from rest_framework import status

class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer

    def create(self, request, *args, **kwargs):
        # Custom logic before creating a goal
        if 'name' not in request.data:
            return Response({"error": "Goal name is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Proceed with the default create method
        return super().create(request, *args, **kwargs)
