"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export default function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/users`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to fetch users");
      const data = await res.json();
      setUsers(data);
    } catch (err: any) {
      setError(err.message || "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const changeRole = async (userId: number, newRole: string) => {
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/users/${userId}/role`, {
        method: "PATCH",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ role: newRole })
      });
      if (!res.ok) throw new Error(await res.text());
      fetchUsers();
    } catch (err: any) {
      alert("Error: " + err.message);
    }
  };

  const deleteUser = async (userId: number) => {
    if (!confirm("Are you sure you want to permanently delete this user? This cannot be undone.")) return;
    try {
      const token = localStorage.getItem("access_token");
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/users/${userId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error(await res.text());
      fetchUsers();
    } catch (err: any) {
      alert("Error: " + err.message);
    }
  };

  if (loading) return <div className="text-white p-8 animate-pulse">Loading User Records...</div>;

  return (
    <div className="space-y-8 animate-in fade-in duration-500 pb-12 max-w-7xl mx-auto">
      {/* Header */}
      <div className="border-b border-ds-border/50 pb-8">
        <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-md bg-ds-elevated border border-ds-border text-text-muted text-[10px] font-semibold uppercase tracking-widest mb-4">
          Access Control
        </div>
        <h1 className="text-3xl md:text-4xl font-medium text-white mb-3 tracking-tight">User Management</h1>
        <p className="text-text-secondary text-base max-w-2xl">
          Complete God-Mode view of all platform users. Promote to Admin or remove users securely.
        </p>
      </div>

      {error && <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg">{error}</div>}

      <div className="glass-panel border border-ds-border rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-ds-elevated/50 border-b border-ds-border text-xs uppercase tracking-widest text-text-muted">
                <th className="px-6 py-4 font-semibold">User</th>
                <th className="px-6 py-4 font-semibold">Role</th>
                <th className="px-6 py-4 font-semibold">Status</th>
                <th className="px-6 py-4 font-semibold">Joined</th>
                <th className="px-6 py-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-ds-border">
              {users.map(user => (
                <tr key={user.id} className="hover:bg-white/5 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-ds-navy flex items-center justify-center font-bold text-white border border-ds-border">
                        {user.username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-white">{user.username}</div>
                        <div className="text-xs text-text-muted">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 rounded text-[10px] font-bold uppercase tracking-widest ${user.role === 'Admin' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-blue-500/10 text-blue-400 border border-blue-500/20'}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex items-center gap-1.5 text-xs text-ds-success">
                      <span className="w-1.5 h-1.5 rounded-full bg-ds-success"></span> Active
                    </span>
                  </td>
                  <td className="px-6 py-4 text-xs text-text-secondary font-mono">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4 text-right space-x-2">
                    {user.role === 'Developer' ? (
                      <button onClick={() => changeRole(user.id, 'Admin')} className="px-3 py-1.5 rounded bg-ds-elevated border border-ds-border text-xs font-semibold text-text-secondary hover:text-white hover:bg-white/10 transition-colors">
                        Promote to Admin
                      </button>
                    ) : (
                      <button onClick={() => changeRole(user.id, 'Developer')} className="px-3 py-1.5 rounded bg-ds-elevated border border-ds-border text-xs font-semibold text-text-secondary hover:text-white hover:bg-white/10 transition-colors">
                        Demote
                      </button>
                    )}
                    <button onClick={() => deleteUser(user.id)} className="px-3 py-1.5 rounded bg-red-500/10 border border-red-500/20 text-xs font-semibold text-red-400 hover:bg-red-500 hover:text-white transition-colors">
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
