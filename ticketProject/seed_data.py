"""Seed script: creates test users, categories, tickets, and messages."""
import random
from django.contrib.auth import get_user_model
from tickets.models import TicketCategory, Ticket, TicketMessage

User = get_user_model()

# ── Create users ──
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
        print(f'  ✓ Created {role}: {uname}')
    else:
        print(f'  - {uname} already exists')

# ── Create categories ──
cat_names = ['Technical Support', 'Billing', 'Account Issue', 'Feature Request', 'General Inquiry']
for name in cat_names:
    TicketCategory.objects.get_or_create(name=name)
print(f'  ✓ {TicketCategory.objects.count()} categories')

# ── Create tickets ──
if Ticket.objects.count() >= 12:
    print(f'  - {Ticket.objects.count()} tickets already exist; skipping ticket creation')
else:
    customers = list(User.objects.filter(role='customer'))
    agents = list(User.objects.filter(role='agent'))
    cats = list(TicketCategory.objects.all())
    statuses = ['OPEN', 'IN_PROGRESS', 'RESOLVED', 'CLOSED']
    priorities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

    topics = ["Login", "Payment", "Error", "Support", "Feature", "Account", "Bug", "Update", "Config", "Access"]

    for i in range(15):
        customer = random.choice(customers)
        agent = random.choice(agents) if random.random() > 0.25 else None
        status = random.choice(statuses)
        priority = random.choice(priorities)
        cat = random.choice(cats) if random.random() > 0.15 else None

        title_words = random.sample(topics, min(3, len(topics)))
        ticket = Ticket.objects.create(
            title=f'Issue #{i+1}: {" ".join(title_words)}',
            description=f'Detailed description for ticket #{i+1}. This issue requires attention from the support team to resolve.',
            status=status,
            priority=priority,
            user=customer,
            assigned_agent=agent,
            category=cat,
        )

        TicketMessage.objects.create(ticket=ticket, sender=customer,
                                      message='I am reporting this issue. Please help me resolve it.')

        if agent:
            TicketMessage.objects.create(ticket=ticket, sender=agent,
                                          message='I have reviewed this ticket and will start working on it.')

        if status in ('RESOLVED', 'CLOSED') and agent:
            TicketMessage.objects.create(ticket=ticket, sender=agent,
                                          message='The issue has been resolved. Please confirm everything works.')
            TicketMessage.objects.create(ticket=ticket, sender=customer,
                                          message='Thank you! The issue is resolved. Appreciate your help.')

    print(f'  ✓ Created {Ticket.objects.count()} tickets')
    print(f'  ✓ Created {TicketMessage.objects.count()} messages')

print('\n✅ Seed data complete!')
print()
print('   Login credentials:')
print('   ───────────────────────────────────')
print('   Admin:    admin1 / Admin123!')
print('   Agent:    agent1 / Agent123!')
print('   Agent:    agent2 / Agent123!')
print('   Customer: customer1 / Cust123!')
print('   Customer: customer2 / Cust123!')
