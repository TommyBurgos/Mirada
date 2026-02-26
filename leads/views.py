from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import Lead
from .serializers import LeadSerializer


@api_view(["POST"])
@permission_classes([AllowAny])  # 🔥 importante: endpoint público
def create_lead(request):
    serializer = LeadSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(
            {"success": True, "message": "Lead registrado correctamente"},
            status=status.HTTP_201_CREATED
        )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)