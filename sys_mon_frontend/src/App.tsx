import React, { useEffect, useState } from 'react';
import './App.css';

interface Machine {
  id: string;
  hostname: string;
  os: string;
  last_checkin: string;
  status: string;
  issues: string[];
  [key: string]: any;
}

const API_BASE = 'http://localhost:8000/api'; // Update if backend runs elsewhere

const statusColors: Record<string, string> = {
  healthy: 'green',
  warning: 'orange',
  critical: 'red',
};

function flagIssues(machine: Machine): string[] {
  const issues: string[] = [];
  if (machine.disk_encrypted === false) issues.push('Unencrypted disk');
  if (machine.os_outdated === true) issues.push('Outdated OS');
  if (machine.antivirus_enabled === false) issues.push('Antivirus off');
  if (machine.sleep_enabled === true) issues.push('Sleep enabled');
  return issues;
}

const App: React.FC = () => {
  const [machines, setMachines] = useState<Machine[]>([]);
  const [filterOS, setFilterOS] = useState('');
  const [filterStatus, setFilterStatus] = useState('');
  const [sortKey, setSortKey] = useState('last_checkin');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');

  useEffect(() => {
    fetch(`${API_BASE}/status`)
      .then(res => res.json())
      .then(data => {
        const withIssues = data.map((m: Machine) => ({
          ...m,
          issues: flagIssues(m),
        }));
        setMachines(withIssues);
      });
  }, []);

  const filtered = machines
    .filter(m => (filterOS ? m.os === filterOS : true))
    .filter(m => (filterStatus ? m.status === filterStatus : true));

  const sorted = [...filtered].sort((a, b) => {
    if (sortKey === 'last_checkin') {
      return sortDir === 'asc'
        ? a.last_checkin.localeCompare(b.last_checkin)
        : b.last_checkin.localeCompare(a.last_checkin);
    }
    if (sortKey === 'hostname') {
      return sortDir === 'asc'
        ? a.hostname.localeCompare(b.hostname)
        : b.hostname.localeCompare(a.hostname);
    }
    return 0;
  });

  const osOptions = Array.from(new Set(machines.map(m => m.os)));
  const statusOptions = Array.from(new Set(machines.map(m => m.status)));

  return (
    <div className="dashboard">
      <h1>System Monitor Admin Dashboard</h1>
      <div className="filters">
        <label>
          OS:
          <select value={filterOS} onChange={e => setFilterOS(e.target.value)}>
            <option value="">All</option>
            {osOptions.map(os => (
              <option key={os} value={os}>{os}</option>
            ))}
          </select>
        </label>
        <label>
          Status:
          <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
            <option value="">All</option>
            {statusOptions.map(status => (
              <option key={status} value={status}>{status}</option>
            ))}
          </select>
        </label>
        <label>
          Sort by:
          <select value={sortKey} onChange={e => setSortKey(e.target.value)}>
            <option value="last_checkin">Last Check-in</option>
            <option value="hostname">Hostname</option>
          </select>
        </label>
        <button onClick={() => setSortDir(d => (d === 'asc' ? 'desc' : 'asc'))}>
          {sortDir === 'asc' ? '↑' : '↓'}
        </button>
      </div>
      <table className="machine-table">
        <thead>
          <tr>
            <th>Hostname</th>
            <th>OS</th>
            <th>Status</th>
            <th>Issues</th>
            <th>Last Check-in</th>
          </tr>
        </thead>
        <tbody>
          {sorted.map(machine => (
            <tr key={machine.id}>
              <td>{machine.hostname}</td>
              <td>{machine.os}</td>
              <td style={{ color: statusColors[machine.status] || 'black' }}>{machine.status}</td>
              <td>
                {machine.issues.length > 0 ? (
                  <ul>
                    {machine.issues.map(issue => (
                      <li key={issue} style={{ color: 'red' }}>{issue}</li>
                    ))}
                  </ul>
                ) : (
                  <span style={{ color: 'green' }}>None</span>
                )}
              </td>
              <td>{new Date(machine.last_checkin).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default App;
