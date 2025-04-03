from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import TermdeCondition
from .serializers import TermdeConditionSerializer

class TermdeConditionListCreateView(generics.ListCreateAPIView):
    queryset = TermdeCondition.objects.all().order_by('-date_creation')
    serializer_class = TermdeConditionSerializer


class TermdeConditionDetailView(APIView):
    def get(self, request, pk, *args, **kwargs):
        term = get_object_or_404(TermdeCondition, pk=pk)
        serializer = TermdeConditionSerializer(term)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        term = get_object_or_404(TermdeCondition, pk=pk)
        serializer = TermdeConditionSerializer(term, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        term = get_object_or_404(TermdeCondition, pk=pk)
        term.delete()
        return Response({"message": "Deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
