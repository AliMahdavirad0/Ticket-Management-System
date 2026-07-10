import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Button from '../components/Button';
import Card from '../components/Card';
import Input from '../components/Input';
import Select from '../components/Select';
import Textarea from '../components/Textarea';
import { useCreateTicket, useCategories } from '../hooks/useTickets';
import type { CreateTicketRequest } from '../api/ticketApi';

export default function CreateTicket() {
  const navigate = useNavigate();
  const mutation = useCreateTicket();
  const { data: categories } = useCategories();
  const [form, setForm] = useState<CreateTicketRequest>({
    title: '',
    description: '',
    priority: 'MEDIUM',
  });
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    if (form.title.trim().length < 5) {
      setError('Title must be at least 5 characters.');
      return;
    }
    if (form.description.trim().length < 10) {
      setError('Description must be at least 10 characters.');
      return;
    }
    setError(null);
    try {
      const ticket = await mutation.mutateAsync(form);
      navigate(`/tickets/${ticket.id}`);
    } catch (err: any) {
      const data = err?.response?.data;
      setError(data?.detail || data?.title?.[0] || data?.description?.[0] || 'Failed to create ticket. Please try again.');
    }
  };

  return (
    <Card className="max-w-2xl mx-auto space-y-4">
      <h1 className="text-2xl font-bold">Create Ticket</h1>

      {error && (
        <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-200">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <Input
          placeholder="Title"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
        />

        <Select
          value={form.priority || 'MEDIUM'}
          onChange={(e) => setForm({ ...form, priority: e.target.value as CreateTicketRequest['priority'] })}
          options={[
            { label: 'Low', value: 'LOW' },
            { label: 'Medium', value: 'MEDIUM' },
            { label: 'High', value: 'HIGH' },
            { label: 'Critical', value: 'CRITICAL' },
          ]}
        />

        <Select
          value={form.category ?? ''}
          onChange={(e) => setForm({ ...form, category: e.target.value ? Number(e.target.value) : undefined })}
          options={[
            { label: 'No category', value: '' },
            ...(categories || []).map((c) => ({ label: c.name, value: c.id })),
          ]}
        />

        <Textarea
          rows={6}
          placeholder="Description"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
        />
      </div>

      <Button onClick={submit} disabled={mutation.isPending}>
        {mutation.isPending ? 'Creating...' : 'Create Ticket'}
      </Button>
    </Card>
  );
}
