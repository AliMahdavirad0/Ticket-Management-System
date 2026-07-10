"""
Seed the database with deterministic demo data.

Usage:
    python manage.py seed_data              # Idempotent seed
    python manage.py seed_data --reset       # Delete all data then seed fresh
"""

import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tickets.models import TicketCategory, Ticket, TicketMessage

User = get_user_model()

SEED = 42  # Deterministic random seed


class Command(BaseCommand):
    help = 'Seed the database with deterministic demo data'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete all data before seeding')

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('  -> Resetting all data...')
            TicketMessage.objects.all().delete()
            Ticket.objects.all().delete()
            TicketCategory.objects.all().delete()
            User.objects.exclude(is_superuser=True).exclude(username='admin1').delete()
            self.stdout.write(self.style.WARNING('  -> Data reset complete.'))

        rng = random.Random(SEED)

        # -- Users ----------------------------------------------------
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
            else:
                self.stdout.write(f'  - {uname} already exists')

        # -- Categories ------------------------------------------------
        cat_names = ['Technical Support', 'Billing', 'Account Issue', 'Feature Request', 'General Inquiry']
        for name in cat_names:
            TicketCategory.objects.get_or_create(name=name)
        self.stdout.write(f'  -> {TicketCategory.objects.count()} categories')

        # -- Tickets ---------------------------------------------------
        existing = Ticket.objects.count()
        if existing >= 15:
            self.stdout.write(f'  - {existing} tickets exist, skipping')
        else:
            customers = list(User.objects.filter(role='customer'))
            agents = list(User.objects.filter(role='agent'))
            cats = list(TicketCategory.objects.all())
            topics = ["Login", "Payment", "Error", "Support", "Feature", "Account", "Bug", "Update", "Config", "Access"]

            # Pre-define a deterministic set of ticket configurations
            # to ensure good coverage of all status/priority/assignment combos
            configs = [
                # (status, priority, has_agent, category_index)
                ('OPEN', 'HIGH', False, 0),
                ('OPEN', 'MEDIUM', False, 1),
                ('IN_PROGRESS', 'CRITICAL', True, 0),
                ('IN_PROGRESS', 'HIGH', True, 2),
                ('IN_PROGRESS', 'LOW', True, None),
                ('RESOLVED', 'MEDIUM', True, 3),
                ('RESOLVED', 'HIGH', True, 1),
                ('CLOSED', 'LOW', True, 0),
                ('CLOSED', 'MEDIUM', True, 4),
                ('OPEN', 'CRITICAL', False, 2),
                ('IN_PROGRESS', 'MEDIUM', True, None),
                ('RESOLVED', 'LOW', True, 3),
                ('CLOSED', 'CRITICAL', True, 4),
                ('OPEN', 'LOW', False, None),
                ('IN_PROGRESS', 'HIGH', True, 0),
            ]

            for i, (status, priority, has_agent, cat_idx) in enumerate(configs):
                customer = rng.choice(customers)
                agent = rng.choice(agents) if has_agent else None
                category = cats[cat_idx] if cat_idx is not None else None

                ticket = Ticket.objects.create(
                    title=f'Issue #{i+1}: {" ".join(rng.sample(topics, 3))}',
                    description=f'Detailed description for ticket #{i+1}. This issue requires attention from the support team to resolve the problem described.',
                    status=status,
                    priority=priority,
                    user=customer,
                    assigned_agent=agent,
                    category=category,
                )

                # Customer opening message
                TicketMessage.objects.create(
                    ticket=ticket, sender=customer,
                    message='I am reporting this issue. Please help me resolve it.'
                )

                # Agent response if assigned
                if agent:
                    TicketMessage.objects.create(
                        ticket=ticket, sender=agent,
                        message='I have reviewed this ticket and will start working on it.'
                    )

                # Resolution messages for resolved/closed tickets
                if status in ('RESOLVED', 'CLOSED') and agent:
                    TicketMessage.objects.create(
                        ticket=ticket, sender=agent,
                        message='The issue has been resolved. Please confirm everything works.'
                    )
                    TicketMessage.objects.create(
                        ticket=ticket, sender=customer,
                        message='Thank you! The issue is resolved. Appreciate your help.'
                    )

            self.stdout.write(f'  -> Created {Ticket.objects.count()} tickets')
            self.stdout.write(f'  -> Created {TicketMessage.objects.count()} messages')

        self.stdout.write(self.style.SUCCESS('\nSeed data complete!'))
        self.stdout.write('')
        self.stdout.write('   Login credentials:')
        self.stdout.write('   --------------------------------')
        self.stdout.write('   Admin:    admin1 / Admin123!')
        self.stdout.write('   Agent:    agent1 / Agent123!')
        self.stdout.write('   Agent:    agent2 / Agent123!')
        self.stdout.write('   Customer: customer1 / Cust123!')
        self.stdout.write('   Customer: customer2 / Cust123!')
        self.stdout.write('')
        self.stdout.write('   URLs:')
        self.stdout.write('   Frontend: http://localhost:5173')
        self.stdout.write('   Swagger:  http://localhost:8000/api/docs/')
        self.stdout.write('   Admin:    http://localhost:8000/admin/')
