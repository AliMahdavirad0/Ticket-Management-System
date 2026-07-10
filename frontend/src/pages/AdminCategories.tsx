import { useState } from 'react';
import Button from '../components/Button';
import Card from '../components/Card';
import Input from '../components/Input';
import { useCategories, useCreateCategory, useDeleteCategory } from '../hooks/useTickets';

export default function AdminCategories() {
  const { data: categories, isLoading } = useCategories();
  const createCategory = useCreateCategory();
  const deleteCategory = useDeleteCategory();
  const [newName, setNewName] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleCreate = () => {
    if (!newName.trim()) return;
    setError(null);
    createCategory.mutate(newName.trim(), {
      onSuccess: () => setNewName(''),
      onError: (err: any) => {
        setError(err?.response?.data?.name?.[0] || 'Failed to create category.');
      },
    });
  };

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Delete category "${name}"? This action cannot be undone.`)) {
      deleteCategory.mutate(id);
    }
  };

  if (isLoading) return <div className="p-6">Loading categories...</div>;

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">Category Management</h1>

      <Card title="Create New Category">
        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-200 mb-4">
            {error}
          </div>
        )}
        <div className="flex gap-3">
          <Input
            placeholder="Category name"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
          />
          <Button
            onClick={handleCreate}
            disabled={createCategory.isPending || !newName.trim()}
          >
            {createCategory.isPending ? 'Creating...' : 'Create'}
          </Button>
        </div>
      </Card>

      <Card title={`Categories (${categories?.length ?? 0})`}>
        {!categories || categories.length === 0 ? (
          <p className="text-gray-400 text-center py-8">No categories yet.</p>
        ) : (
          <div className="space-y-2">
            {categories.map((cat) => (
              <div
                key={cat.id}
                className="flex items-center justify-between border rounded-lg p-3"
              >
                <span className="font-medium">{cat.name}</span>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => handleDelete(cat.id, cat.name)}
                  isLoading={deleteCategory.isPending}
                >
                  Delete
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
