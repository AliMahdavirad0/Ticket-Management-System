from django.urls import path

from .views import DashboardOverviewView, AdminAgentWorkloadView

urlpatterns = [
    path('', DashboardOverviewView.as_view(), name='dashboard-overview'),
    path('agents/', AdminAgentWorkloadView.as_view(), name='dashboard-agents'),
]
