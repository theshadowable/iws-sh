import React, { useState, useEffect } from 'react';
import { Plus, Search, Filter, Ticket, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';

const SupportTickets = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const navigate = useNavigate();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchTickets();
  }, [statusFilter, categoryFilter]);

  const fetchTickets = async () => {
    try {
      const token = localStorage.getItem('token');
      let url = `${BACKEND_URL}/api/tickets?limit=100`;
      
      if (statusFilter !== 'all') {
        url += `&status=${statusFilter}`;
      }
      if (categoryFilter !== 'all') {
        url += `&category=${categoryFilter}`;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTickets(data.tickets);
      }
    } catch (error) {
      console.error('Error fetching tickets:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      'open': { bg: 'bg-blue-100', text: 'text-blue-800', icon: Clock, label: 'Open' },
      'in_progress': { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: Clock, label: 'In Progress' },
      'resolved': { bg: 'bg-green-100', text: 'text-green-800', icon: CheckCircle, label: 'Resolved' },
      'approve': { bg: 'bg-orange-100', text: 'text-orange-800', icon: AlertCircle, label: 'Approve' },
      'closed': { bg: 'bg-gray-100', text: 'text-gray-800', icon: CheckCircle, label: 'Closed' }
    };
    return badges[status] || badges['open'];
  };

  const getPriorityBadge = (priority) => {
    const badges = {
      'low': { bg: 'bg-gray-100', text: 'text-gray-700', label: 'Low' },
      'medium': { bg: 'bg-blue-100', text: 'text-blue-700', label: 'Medium' },
      'high': { bg: 'bg-orange-100', text: 'text-orange-700', label: 'High' },
      'critical': { bg: 'bg-red-100', text: 'text-red-700', label: 'Critical' }
    };
    return badges[priority] || badges['medium'];
  };

  const getCategoryLabel = (category) => {
    const labels = {
      'technical_issue': 'Technical Issue',
      'water_quality': 'Water Quality',
      'maintenance_repairs': 'Maintenance & Repairs',
      'general_inquiry': 'General Inquiry'
    };
    return labels[category] || category;
  };

  const filteredTickets = tickets.filter(ticket =>
    ticket.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ticket.ticket_number.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Support Tickets</h1>
            <p className="text-gray-600 mt-1">Manage your support requests</p>
          </div>
          <button
            onClick={() => navigate('/tickets/create')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Plus className="w-5 h-5" />
            Create Ticket
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
            <p className="text-gray-600 text-sm">Total Tickets</p>
            <p className="text-2xl font-bold text-gray-900">{tickets.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-yellow-500">
            <p className="text-gray-600 text-sm">In Progress</p>
            <p className="text-2xl font-bold text-gray-900">
              {tickets.filter(t => t.status === 'in_progress').length}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
            <p className="text-gray-600 text-sm">Resolved</p>
            <p className="text-2xl font-bold text-gray-900">
              {tickets.filter(t => t.status === 'resolved').length}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4 border-l-4 border-orange-500">
            <p className="text-gray-600 text-sm">Awaiting Approval</p>
            <p className="text-2xl font-bold text-gray-900">
              {tickets.filter(t => t.status === 'approve').length}
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search tickets by number or subject..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Status Filter */}
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Status</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="approve">Approve</option>
              <option value="closed">Closed</option>
            </select>

            {/* Category Filter */}
            <select
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Categories</option>
              <option value="technical_issue">Technical Issue</option>
              <option value="water_quality">Water Quality</option>
              <option value="maintenance_repairs">Maintenance & Repairs</option>
              <option value="general_inquiry">General Inquiry</option>
            </select>
          </div>
        </div>

        {/* Tickets List */}
        <div className="bg-white rounded-lg shadow">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="text-gray-600 mt-4">Loading tickets...</p>
            </div>
          ) : filteredTickets.length === 0 ? (
            <div className="p-8 text-center">
              <Ticket className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 text-lg font-medium">No tickets found</p>
              <p className="text-gray-500 mt-2">Create your first support ticket to get started</p>
              <button
                onClick={() => navigate('/tickets/create')}
                className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Create Ticket
              </button>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredTickets.map((ticket) => {
                const statusBadge = getStatusBadge(ticket.status);
                const priorityBadge = getPriorityBadge(ticket.priority);
                const StatusIcon = statusBadge.icon;

                return (
                  <div
                    key={ticket.id}
                    onClick={() => navigate(`/tickets/${ticket.id}`)}
                    className="p-6 hover:bg-gray-50 cursor-pointer transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="font-mono text-sm font-bold text-blue-600">
                            #{ticket.ticket_number}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusBadge.bg} ${statusBadge.text} flex items-center gap-1`}>
                            <StatusIcon className="w-3 h-3" />
                            {statusBadge.label}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${priorityBadge.bg} ${priorityBadge.text}`}>
                            {priorityBadge.label}
                          </span>
                          <span className="text-xs text-gray-500">
                            {getCategoryLabel(ticket.category)}
                          </span>
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                          {ticket.subject}
                        </h3>
                        <p className="text-gray-600 text-sm line-clamp-2">
                          {ticket.description}
                        </p>
                        <div className="flex items-center gap-4 mt-3 text-xs text-gray-500">
                          <span>Created {new Date(ticket.created_at).toLocaleDateString()}</span>
                          {ticket.assigned_to_name && (
                            <span>Assigned to: {ticket.assigned_to_name}</span>
                          )}
                          {ticket.messages_count > 0 && (
                            <span>{ticket.messages_count} messages</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default SupportTickets;
