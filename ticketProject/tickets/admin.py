from django.contrib import admin
from .models import Ticket, TicketCategory, TicketMessage

admin.site.register(Ticket)
admin.site.register(TicketCategory)
admin.site.register(TicketMessage)
