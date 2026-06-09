from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin
from .services import DashboardService
from .serializers import DashboardOverviewSerializer, AgentWorkloadSerializer


class DashboardOverviewView(APIView):
    """
    Role-based dashboard overview.

    Returns ticket/message stats, recent activity, and extra metrics
    for admin, agent, or customer roles.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = DashboardService.get_overview(request.user)
        serializer = DashboardOverviewSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class AdminAgentWorkloadView(APIView):
    """Agent workload breakdown (admin only)."""

    permission_classes = [IsAdmin]

    def get(self, request):
        workload = DashboardService.get_agent_workload()
        serializer = AgentWorkloadSerializer(workload, many=True)
        return Response(serializer.data)
