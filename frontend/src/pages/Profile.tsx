import { useState } from 'react';
import Button from '../components/Button';
import Card from '../components/Card';
import Input from '../components/Input';
import Badge from '../components/Badge';
import { useUserProfile, useUpdateProfile, useChangePassword } from '../hooks/useAuth';

export default function Profile() {
  const { data: profile, isLoading } = useUserProfile();
  const updateProfile = useUpdateProfile();
  const changePassword = useChangePassword();

  const [editMode, setEditMode] = useState(false);
  const [form, setForm] = useState({ first_name: '', last_name: '', email: '' });
  const [pwForm, setPwForm] = useState({ old_password: '', new_password: '', new_password2: '' });
  const [pwError, setPwError] = useState<string | null>(null);
  const [pwSuccess, setPwSuccess] = useState(false);

  if (isLoading) return <div className="p-6">Loading profile...</div>;
  if (!profile) return <div className="p-6">Could not load profile.</div>;

  const roleVariant = profile.role === 'admin' ? 'danger' : profile.role === 'agent' ? 'warning' : 'info';

  const handleSaveProfile = () => {
    updateProfile.mutate(form, {
      onSuccess: () => setEditMode(false),
    });
  };

  const startEdit = () => {
    setForm({
      first_name: profile.first_name || '',
      last_name: profile.last_name || '',
      email: profile.email || '',
    });
    setEditMode(true);
  };

  const handleChangePassword = () => {
    setPwError(null);
    setPwSuccess(false);

    if (pwForm.new_password !== pwForm.new_password2) {
      setPwError('Passwords do not match.');
      return;
    }

    changePassword.mutate(pwForm, {
      onSuccess: () => {
        setPwForm({ old_password: '', new_password: '', new_password2: '' });
        setPwSuccess(true);
      },
      onError: (err: any) => {
        const data = err?.response?.data;
        if (data) {
          const msgs = Object.entries(data)
            .map(([, v]) => (Array.isArray(v) ? v.join(', ') : String(v)))
            .join('; ');
          setPwError(msgs || 'Failed to change password.');
        } else {
          setPwError('Failed to change password.');
        }
      },
    });
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold">My Profile</h1>

      {/* Profile info card */}
      <Card>
        <div className="flex items-start justify-between">
          <div className="space-y-1">
            <div className="flex items-center gap-3">
              <span className="text-2xl font-semibold">{profile.username}</span>
              <Badge variant={roleVariant}>{profile.role}</Badge>
            </div>
            <p className="text-gray-500">{profile.email}</p>
            <p className="text-sm text-gray-400">
              Joined {new Date(profile.date_joined).toLocaleDateString()}
            </p>
          </div>
          {!editMode && (
            <Button variant="secondary" onClick={startEdit}>
              Edit Profile
            </Button>
          )}
        </div>

        {editMode && (
          <div className="mt-6 border-t pt-4 space-y-3">
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="First Name"
                value={form.first_name}
                onChange={(e) => setForm({ ...form, first_name: e.target.value })}
              />
              <Input
                label="Last Name"
                value={form.last_name}
                onChange={(e) => setForm({ ...form, last_name: e.target.value })}
              />
            </div>
            <Input
              label="Email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
            <div className="flex gap-3">
              <Button onClick={handleSaveProfile} isLoading={updateProfile.isPending}>
                Save
              </Button>
              <Button variant="secondary" onClick={() => setEditMode(false)}>
                Cancel
              </Button>
            </div>
          </div>
        )}
      </Card>

      {/* Ticket stats */}
      <Card title="My Ticket Statistics">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {Object.entries(profile.statistics).map(([key, value]) => (
            <div key={key}>
              <p className="text-gray-500 text-sm capitalize">
                {key.replace(/_/g, ' ')}
              </p>
              <p className="text-2xl font-bold mt-1">{value}</p>
            </div>
          ))}
          {Object.keys(profile.statistics).length === 0 && (
            <p className="text-gray-400 col-span-full">No statistics available.</p>
          )}
        </div>
      </Card>

      {/* Change password */}
      <Card title="Change Password">
        {pwSuccess && (
          <div className="bg-green-50 text-green-700 p-3 rounded-lg text-sm border border-green-200 mb-4">
            Password changed successfully.
          </div>
        )}
        {pwError && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm border border-red-200 mb-4">
            {pwError}
          </div>
        )}
        <div className="space-y-3">
          <Input
            type="password"
            label="Current Password"
            value={pwForm.old_password}
            onChange={(e) => setPwForm({ ...pwForm, old_password: e.target.value })}
          />
          <Input
            type="password"
            label="New Password"
            value={pwForm.new_password}
            onChange={(e) => setPwForm({ ...pwForm, new_password: e.target.value })}
          />
          <Input
            type="password"
            label="Confirm New Password"
            value={pwForm.new_password2}
            onChange={(e) => setPwForm({ ...pwForm, new_password2: e.target.value })}
          />
          <Button
            onClick={handleChangePassword}
            isLoading={changePassword.isPending}
            disabled={!pwForm.old_password || !pwForm.new_password || !pwForm.new_password2}
          >
            Change Password
          </Button>
        </div>
      </Card>
    </div>
  );
}
