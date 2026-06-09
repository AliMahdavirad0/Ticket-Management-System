from rest_framework.routers import DefaultRouter
from .views import TicketViewSet, TicketCategoryViewSet, TicketMessageViewSet

router = DefaultRouter()

router.register("tickets", TicketViewSet, basename="ticket")
router.register("categories", TicketCategoryViewSet)
router.register("messages", TicketMessageViewSet,basename="messages")

urlpatterns = router.urls
