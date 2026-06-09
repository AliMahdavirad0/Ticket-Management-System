import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tickets.models import TicketCategory, Ticket, TicketMessage

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with test data'

    def handle(self, *args, **options):
        # Users
        users_data = [
            ('admin1', 'admin@example.com', 'Admin123!', 'admin', '', ''),
            ('agent1', 'agent1@example.com', 'Agent123!', 'agent', 'Alice', 'Smith'),
            ('agent2', 'agent2@example.com', 'Agent123!', 'agent', 'Bob', 'Jones'),
            ('customer1', 'cust1@example.com', 'Cust123!', 'customer', 'Charlie', 'Brown'),
            ('customer2', 'cust2@example.com', 'Cust123!', 'customer', 'Diana', 'Prince'),
        ]
        for uname, email, pw, role, fn, ln in users_data:
            if not User.objects.filter(username=uname).exists():
                if role == 'admin':
                    User.objects.create_superuser(uname, email, pw, role=role, first_name=fn, last_name=ln)
                else:
                    User.objects.create_user(uname, email, pw, role=role, first_name=fn, last_name=ln)
                self.stdout.write(f'  -> Created {role}: {uname}')

        # Categories
        cat_names = ['Technical Support', 'Billing', 'Account Issue', 'Feature Request', 'General Inquiry']
        for name in cat_names:
            TicketCategory.objects.get_or_create(name=name)
        self.stdout.write(f'  -> {TicketCategory.objects.count()} categories')

        # Tickets
        if Ticket.objects.count() >= 12:
            self.stdout.write(f'  - {Ticket.objects.count()} tickets exist, skipping')
        else:
            customers = list(User.objects.filter(role='customer'))
            agents = list(User.objects.filter(role='agent'))
            cats = list(TicketCategory.objects.all())
            topics = ["Login", "Payment", "Error", "Support", "Feature", "Account", "Bug", "Update", "Config", "Access"]
            statuses = ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']
            priorities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

            for i in range(15):
                customer = random.choice(customers)
                agent = random.choice(agents) if random.random() > 0.25 else None
                ticket = Ticket.objects.create(
                    title=f'Issue #{i+1}: {" ".join(random.sample(topics, 3))}',
                    description=f'Detailed description for ticket #{i+1}. This issue requires attention from the support team to resolve the problem described.',
                    status=random.choice(statuses),
                    priority=random.choice(priorities),
                    user=customer,
                    assigned_agent=agent,
                    category=random.choice(cats) if random.random() > 0.15 else None,
                )
                TicketMessage.objects.create(ticket=ticket, sender=customer, message='I am reporting this issue. Please help me resolve it.')
                if agent:
                    TicketMessage.objects.create(ticket=ticket, sender=agent, message='I have reviewed this ticket and will start working on it.')
                if ticket.status in ('RESOLVED', 'CLOSED') and agent:
                    TicketMessage.objects.create(ticket=ticket, sender=agent, message='The issue has been resolved. Please confirm everything works.')
                    TicketMessage.objects.create(ticket=ticket, sender=customer, message='Thank you! The issue is resolved. Appreciate your help.')

            self.stdout.write(f'  -> Created {Ticket.objects.count()} tickets')
            self.stdout.write(f'  -> Created {TicketMessage.objects.count()} messages')

        self.stdout.write(self.style.SUCCESS('\nSeed data created!'))
        self.stdout.write('')
        self.stdout.write('   Login credentials:')
        self.stdout.write('   Admin:    admin1 / Admin123!')
        self.stdout.write('   Agent:    agent1 / Agent123!')
        self.stdout.write('   Agent:    agent2 / Agent123!')
        self.stdout.write('   Customer: customer1 / Cust123!')
        self.stdout.write('   Customer: customer2 / Cust123!')
