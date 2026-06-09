import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/Button';
import Card from '../components/Card';
import Input from '../components/Input';
import Select from '../components/Select';
import Textarea from '../components/Textarea';
import { useCreateTicket } from '../hooks/useTickets';
import type { CreateTicketRequest } from '../api/ticketApi';

export default function CreateTicket() {
  const navigate = useNavigate();
  const mutation = useCreateTicket();
  const [form, setForm] = useState<CreateTicketRequest>({
    title: '',
    description: '',
    priority: 'MEDIUM',
  });

  const submit = async () => {
    const ticket = await mutation.mutateAsync(form);
    navigate(`/tickets/${ticket.id}`);
  };

  return (
    <Card className="max-w-2xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold">Create Ticket</h1>

      <Input placeholder="Title" value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />

      <Select value={form.priority} onChange={(e) => setForm({ ...form, priority: e.target.value as CreateTicketRequest['priority'] })} options={[{label:"LOW",value:"LOW"},{label:"MEDIUM",value:"MEDIUM"},{label:"HIGH",value:"HIGH"},{label:"CRITICAL",value:"CRITICAL"}]} />

      <Textarea rows={6} placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />

      <Button onClick={submit} disabled={mutation.isPending}>
        {mutation.isPending ? 'Creating...' : 'Create'}
      </Button>
    </Card>
  );
}
