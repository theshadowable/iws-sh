import React, { useState, useEffect } from 'react';
import { 
  Search, Filter, Ticket, Clock, CheckCircle, XCircle, AlertCircle, 
  User, Calendar, MessageSquare, Paperclip, FileSignature, MapPin,
  ChevronDown, ChevronUp, Eye, UserPlus, RefreshCw, Send
} from 'lucide-react';
import { Layout } from '../components/Layout';
import toast from 'react-hot-toast';

const AdminTickets = () => {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [stats, setStats] = useState(null);
  const [technicians, setTechnicians] = useState([]);
  
  // Modal states
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [showReplyModal, setShowReplyModal] = useState(false);
  const [showApprovalModal, setShowApprovalModal] = useState(false);
  
  // Form states
  const [assignTo, setAssignTo] = useState('');
  const [replyMessage, setReplyMessage] = useState('');
  const [isInternalMessage, setIsInternalMessage] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [statusNotes, setStatusNotes] = useState('');
  
  // Detail tab state
  const [activeTab, setActiveTab] = useState('info');
  const [messages, setMessages] = useState([]);
  const [attachments, setAttachments] = useState([]);

  // Use relative URLs to avoid mixed content issues - frontend and backend are on same domain
  const API_BASE = '/api';

  useEffect(() => {
    fetchStats();
    fetchTickets();
    fetchTechnicians();
  }, [statusFilter, categoryFilter, priorityFilter]);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/tickets/admin/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const fetchTickets = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      let url = `${API_BASE}/tickets?limit=100`;
      
      if (statusFilter !== 'all') url += `&status=${statusFilter}`;
      if (categoryFilter !== 'all') url += `&category=${categoryFilter}`;
      if (priorityFilter !== 'all') url += `&priority=${priorityFilter}`;

      const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const data = await response.json();
        setTickets(data.tickets || []);
      } else {
        console.error('Failed to fetch tickets:', response.status);
        // Don't show error toast on empty data (404)
        if (response.status !== 404) {
          toast.error('Failed to load tickets');
        }
      }
    } catch (error) {
      console.error('Error fetching tickets:', error);
      // Only show toast for network errors, not HTTP errors (already handled above)
    } finally {
      setLoading(false);
    }
  };

  const fetchTechnicians = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/users?role=technician`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setTechnicians(data.users || []);
      }
    } catch (error) {
      console.error('Error fetching technicians:', error);
    }
  };

  const viewTicketDetail = async (ticket) => {
    setSelectedTicket(ticket);
    setShowDetailModal(true);
    setActiveTab('info');
    
    // Fetch messages
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/tickets/${ticket.id}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
    
    // Set attachments from ticket
    setAttachments(ticket.attachments || []);
  };

  const handleAssignTicket = async () => {
    if (!assignTo) {
      toast.error('Please select a technician');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/tickets/${selectedTicket.id}/assign`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ assigned_to: assignTo })
      });

      if (response.ok) {
        toast.success('Ticket assigned successfully');
        setShowAssignModal(false);
        setAssignTo('');
        fetchTickets();
        fetchStats();
      } else {
        toast.error('Failed to assign ticket');
      }
    } catch (error) {
      console.error('Error assigning ticket:', error);
      toast.error('Error assigning ticket');
    }
  };

  const handleReplyMessage = async () => {
    if (!replyMessage.trim()) {
      toast.error('Please enter a message');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/tickets/${selectedTicket.id}/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          message: replyMessage,
          is_internal: isInternalMessage 
        })
      });

      if (response.ok) {
        toast.success('Message sent successfully');
        setReplyMessage('');
        setIsInternalMessage(false);
        setShowReplyModal(false);
        
        // Refresh messages
        const messagesResponse = await fetch(`${API_BASE}/tickets/${selectedTicket.id}/messages`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (messagesResponse.ok) {
          const data = await messagesResponse.json();
          setMessages(data);
        }
      } else {
        toast.error('Failed to send message');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      toast.error('Error sending message');
    }
  };

  const handleUpdateStatus = async () => {
    if (!newStatus) {
      toast.error('Please select a status');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE}/tickets/${selectedTicket.id}/status`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          status: newStatus,
          notes: statusNotes 
        })
      });

      if (response.ok) {
        toast.success('Status updated successfully');
        setNewStatus('');
        setStatusNotes('');
        setShowApprovalModal(false);
        fetchTickets();
        fetchStats();
        
        // Update selected ticket
        const updatedResponse = await fetch(`${API_BASE}/tickets/${selectedTicket.id}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (updatedResponse.ok) {
          const updatedTicket = await updatedResponse.json();
          setSelectedTicket(updatedTicket);
        }
      } else {
        toast.error('Failed to update status');
      }
    } catch (error) {
      console.error('Error updating status:', error);
      toast.error('Error updating status');
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      'open': { bg: 'bg-blue-100', text: 'text-blue-800', icon: Clock, label: 'Open' },
      'in_progress': { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: Clock, label: 'In Progress' },
      'resolved': { bg: 'bg-green-100', text: 'text-green-800', icon: CheckCircle, label: 'Resolved' },
      'approve': { bg: 'bg-orange-100', text: 'text-orange-800', icon: AlertCircle, label: 'Pending Approval' },
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

  const needsApproval = (ticket) => {
    return ticket.category === 'maintenance_repairs' && 
           ticket.status === 'resolved' && 
           ticket.attachments?.length > 0;
  };

  const filteredTickets = tickets.filter(ticket =>
    ticket.subject?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ticket.ticket_number?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ticket.customer_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <Layout>
      <div className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Support Tickets Management</h1>
            <p className="text-gray-600 mt-1">Manage and track all support requests</p>
          </div>
          <button
            onClick={fetchTickets}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <RefreshCw className="w-5 h-5" />
            Refresh
          </button>
        </div>

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Total Tickets</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.total_tickets}</p>
                </div>
                <Ticket className="w-8 h-8 text-blue-600" />
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Open</p>
                  <p className="text-2xl font-bold text-blue-600">{stats.open_tickets}</p>
                </div>
                <Clock className="w-8 h-8 text-blue-600" />
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">In Progress</p>
                  <p className="text-2xl font-bold text-yellow-600">{stats.in_progress_tickets}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-600" />
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Resolved</p>
                  <p className="text-2xl font-bold text-green-600">{stats.resolved_tickets}</p>
                </div>
                <CheckCircle className="w-8 h-8 text-green-600" />
              </div>
            </div>
            
            <div className="bg-white p-4 rounded-lg shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Critical</p>
                  <p className="text-2xl font-bold text-red-600">{stats.critical_tickets}</p>
                </div>
                <AlertCircle className="w-8 h-8 text-red-600" />
              </div>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg shadow mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Search tickets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
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
              <option value="approve">Pending Approval</option>
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

            {/* Priority Filter */}
            <select
              value={priorityFilter}
              onChange={(e) => setPriorityFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="all">All Priorities</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>
        </div>

        {/* Tickets Table */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Loading tickets...</p>
            </div>
          ) : filteredTickets.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              <Ticket className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p>No tickets found</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ticket #</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Subject</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Category</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Priority</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Assigned To</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredTickets.map((ticket) => {
                    const StatusBadge = getStatusBadge(ticket.status);
                    const PriorityBadge = getPriorityBadge(ticket.priority);
                    
                    return (
                      <tr key={ticket.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="font-mono text-sm font-medium text-gray-900">
                            {ticket.ticket_number}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="text-sm font-medium text-gray-900 max-w-xs truncate">
                            {ticket.subject}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">{ticket.customer_name}</div>
                          <div className="text-xs text-gray-500">{ticket.customer_email}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className="text-sm text-gray-600">
                            {getCategoryLabel(ticket.category)}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${PriorityBadge.bg} ${PriorityBadge.text}`}>
                            {PriorityBadge.label}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${StatusBadge.bg} ${StatusBadge.text}`}>
                            <StatusBadge.icon className="w-3 h-3 mr-1" />
                            {StatusBadge.label}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-gray-900">
                            {ticket.assigned_to_name || (
                              <span className="text-gray-400 italic">Unassigned</span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(ticket.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                          <div className="flex gap-2">
                            <button
                              onClick={() => viewTicketDetail(ticket)}
                              className="text-blue-600 hover:text-blue-900 transition-colors"
                              title="View Details"
                            >
                              <Eye className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => {
                                setSelectedTicket(ticket);
                                setShowAssignModal(true);
                              }}
                              className="text-green-600 hover:text-green-900 transition-colors"
                              title="Assign Ticket"
                            >
                              <UserPlus className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => {
                                setSelectedTicket(ticket);
                                setShowReplyModal(true);
                              }}
                              className="text-purple-600 hover:text-purple-900 transition-colors"
                              title="Reply"
                            >
                              <MessageSquare className="w-5 h-5" />
                            </button>
                            {needsApproval(ticket) && (
                              <button
                                onClick={() => {
                                  setSelectedTicket(ticket);
                                  setNewStatus('approve');
                                  setShowApprovalModal(true);
                                }}
                                className="text-orange-600 hover:text-orange-900 transition-colors animate-pulse"
                                title="Needs Approval"
                              >
                                <AlertCircle className="w-5 h-5" />
                              </button>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Detail Modal */}
        {showDetailModal && selectedTicket && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
              {/* Modal Header */}
              <div className="px-6 py-4 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">
                      Ticket #{selectedTicket.ticket_number}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">{selectedTicket.subject}</p>
                  </div>
                  <button
                    onClick={() => setShowDetailModal(false)}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <XCircle className="w-6 h-6" />
                  </button>
                </div>
              </div>

              {/* Tabs */}
              <div className="flex border-b border-gray-200">
                {['info', 'messages', 'attachments'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-6 py-3 text-sm font-medium capitalize ${
                      activeTab === tab
                        ? 'border-b-2 border-blue-600 text-blue-600'
                        : 'text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div className="flex-1 overflow-y-auto p-6">
                {activeTab === 'info' && (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium text-gray-700">Customer</label>
                        <p className="mt-1 text-gray-900">{selectedTicket.customer_name}</p>
                        <p className="text-sm text-gray-500">{selectedTicket.customer_email}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Assigned To</label>
                        <p className="mt-1 text-gray-900">
                          {selectedTicket.assigned_to_name || <span className="text-gray-400 italic">Unassigned</span>}
                        </p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Category</label>
                        <p className="mt-1 text-gray-900">{getCategoryLabel(selectedTicket.category)}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Priority</label>
                        <div className="mt-1">
                          {(() => {
                            const badge = getPriorityBadge(selectedTicket.priority);
                            return (
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
                                {badge.label}
                              </span>
                            );
                          })()}
                        </div>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Status</label>
                        <div className="mt-1">
                          {(() => {
                            const badge = getStatusBadge(selectedTicket.status);
                            return (
                              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}>
                                <badge.icon className="w-3 h-3 mr-1" />
                                {badge.label}
                              </span>
                            );
                          })()}
                        </div>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Created At</label>
                        <p className="mt-1 text-gray-900">
                          {new Date(selectedTicket.created_at).toLocaleString()}
                        </p>
                      </div>
                    </div>
                    
                    <div>
                      <label className="text-sm font-medium text-gray-700">Description</label>
                      <p className="mt-1 text-gray-900 whitespace-pre-wrap bg-gray-50 p-4 rounded-lg">
                        {selectedTicket.description}
                      </p>
                    </div>

                    {selectedTicket.gps_coordinates && (
                      <div>
                        <label className="text-sm font-medium text-gray-700 flex items-center gap-2">
                          <MapPin className="w-4 h-4" />
                          GPS Location
                        </label>
                        <p className="mt-1 text-gray-900">
                          Lat: {selectedTicket.gps_coordinates.latitude}, 
                          Lng: {selectedTicket.gps_coordinates.longitude}
                          {selectedTicket.gps_coordinates.accuracy && 
                            ` (±${selectedTicket.gps_coordinates.accuracy}m)`
                          }
                        </p>
                      </div>
                    )}

                    {/* Quick Actions */}
                    <div className="flex gap-3 pt-4 border-t">
                      <button
                        onClick={() => {
                          setShowDetailModal(false);
                          setShowAssignModal(true);
                        }}
                        className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2"
                      >
                        <UserPlus className="w-4 h-4" />
                        Assign Technician
                      </button>
                      <button
                        onClick={() => {
                          setShowDetailModal(false);
                          setShowReplyModal(true);
                        }}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                      >
                        <Send className="w-4 h-4" />
                        Reply
                      </button>
                      <button
                        onClick={() => {
                          setShowDetailModal(false);
                          setShowApprovalModal(true);
                        }}
                        className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2"
                      >
                        <CheckCircle className="w-4 h-4" />
                        Update Status
                      </button>
                    </div>
                  </div>
                )}

                {activeTab === 'messages' && (
                  <div className="space-y-4">
                    {messages.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <MessageSquare className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <p>No messages yet</p>
                      </div>
                    ) : (
                      messages.map((message) => (
                        <div
                          key={message.id}
                          className={`p-4 rounded-lg ${
                            message.is_internal 
                              ? 'bg-yellow-50 border border-yellow-200' 
                              : 'bg-gray-50'
                          }`}
                        >
                          <div className="flex items-start justify-between mb-2">
                            <div>
                              <span className="font-medium text-gray-900">{message.user_name}</span>
                              <span className={`ml-2 text-xs px-2 py-1 rounded ${
                                message.user_role === 'admin' ? 'bg-red-100 text-red-700' :
                                message.user_role === 'technician' ? 'bg-blue-100 text-blue-700' :
                                'bg-gray-100 text-gray-700'
                              }`}>
                                {message.user_role}
                              </span>
                              {message.is_internal && (
                                <span className="ml-2 text-xs px-2 py-1 rounded bg-yellow-100 text-yellow-700">
                                  Internal
                                </span>
                              )}
                            </div>
                            <span className="text-xs text-gray-500">
                              {new Date(message.created_at).toLocaleString()}
                            </span>
                          </div>
                          <p className="text-gray-700 whitespace-pre-wrap">{message.message}</p>
                        </div>
                      ))
                    )}
                  </div>
                )}

                {activeTab === 'attachments' && (
                  <div className="space-y-4">
                    {attachments.length === 0 ? (
                      <div className="text-center py-8 text-gray-500">
                        <Paperclip className="w-12 h-12 mx-auto mb-4 text-gray-400" />
                        <p>No attachments</p>
                      </div>
                    ) : (
                      attachments.map((attachment) => (
                        <div key={attachment.id} className="p-4 bg-gray-50 rounded-lg">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                              <Paperclip className="w-5 h-5 text-gray-400" />
                              <div>
                                <p className="font-medium text-gray-900">{attachment.file_name}</p>
                                <p className="text-xs text-gray-500">
                                  {(attachment.file_size / 1024).toFixed(2)} KB • 
                                  {new Date(attachment.uploaded_at).toLocaleDateString()}
                                </p>
                                {attachment.gps_coordinates && (
                                  <p className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                                    <MapPin className="w-3 h-3" />
                                    GPS: {attachment.gps_coordinates.latitude}, {attachment.gps_coordinates.longitude}
                                  </p>
                                )}
                              </div>
                            </div>
                            <a
                              href={`${API_BASE}/tickets/${selectedTicket.id}/attachments/${attachment.id}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
                            >
                              Download
                            </a>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Assign Modal */}
        {showAssignModal && selectedTicket && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-bold text-gray-900">Assign Ticket</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Ticket #{selectedTicket.ticket_number}
                </p>
              </div>
              <div className="p-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Technician
                </label>
                <select
                  value={assignTo}
                  onChange={(e) => setAssignTo(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">-- Select Technician --</option>
                  {technicians.map((tech) => (
                    <option key={tech.id} value={tech.id}>
                      {tech.full_name} - {tech.email}
                    </option>
                  ))}
                </select>
              </div>
              <div className="px-6 py-4 bg-gray-50 flex gap-3 justify-end">
                <button
                  onClick={() => {
                    setShowAssignModal(false);
                    setAssignTo('');
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAssignTicket}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Assign
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Reply Modal */}
        {showReplyModal && selectedTicket && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-bold text-gray-900">Reply to Ticket</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Ticket #{selectedTicket.ticket_number}
                </p>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Message
                  </label>
                  <textarea
                    value={replyMessage}
                    onChange={(e) => setReplyMessage(e.target.value)}
                    rows={6}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Type your message here..."
                  />
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="internal"
                    checked={isInternalMessage}
                    onChange={(e) => setIsInternalMessage(e.target.checked)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <label htmlFor="internal" className="ml-2 text-sm text-gray-700">
                    Internal message (not visible to customer)
                  </label>
                </div>
              </div>
              <div className="px-6 py-4 bg-gray-50 flex gap-3 justify-end">
                <button
                  onClick={() => {
                    setShowReplyModal(false);
                    setReplyMessage('');
                    setIsInternalMessage(false);
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleReplyMessage}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  Send Message
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Status Update Modal */}
        {showApprovalModal && selectedTicket && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-bold text-gray-900">Update Ticket Status</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Ticket #{selectedTicket.ticket_number}
                </p>
              </div>
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    New Status
                  </label>
                  <select
                    value={newStatus}
                    onChange={(e) => setNewStatus(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">-- Select Status --</option>
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="resolved">Resolved</option>
                    <option value="approve">Pending Approval</option>
                    <option value="closed">Closed</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes (Optional)
                  </label>
                  <textarea
                    value={statusNotes}
                    onChange={(e) => setStatusNotes(e.target.value)}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="Add any notes about this status change..."
                  />
                </div>
                
                {/* Warning for maintenance_repairs approval */}
                {selectedTicket.category === 'maintenance_repairs' && newStatus === 'approve' && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex items-start gap-2">
                      <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                      <div className="text-sm text-yellow-800">
                        <p className="font-medium">Maintenance & Repairs Approval</p>
                        <p className="mt-1">
                          Please verify that the technician has attached:
                        </p>
                        <ul className="list-disc list-inside mt-2 space-y-1">
                          <li>Photos with GPS metadata and timestamp</li>
                          <li>Required documents</li>
                          <li>Digital signature</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              <div className="px-6 py-4 bg-gray-50 flex gap-3 justify-end">
                <button
                  onClick={() => {
                    setShowApprovalModal(false);
                    setNewStatus('');
                    setStatusNotes('');
                  }}
                  className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleUpdateStatus}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Update Status
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default AdminTickets;
