import React, { useState, useEffect } from 'react';
import { ArrowLeft, Send, Paperclip, MapPin, Clock, User, Tag, AlertCircle, Download, FileText, Image as ImageIcon } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import Layout from '../components/Layout';
import TicketStatusTimeline from '../components/TicketStatusTimeline';
import SignaturePad from '../components/SignaturePad';

const TicketDetail = () => {
  const [ticket, setTicket] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sendingMessage, setSendingMessage] = useState(false);
  const [showSignaturePad, setShowSignaturePad] = useState(false);
  const { id } = useParams();
  const navigate = useNavigate();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchTicketDetail();
    fetchMessages();
  }, [id]);

  const fetchTicketDetail = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/tickets/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setTicket(data);
      } else {
        navigate('/tickets');
      }
    } catch (error) {
      console.error('Error fetching ticket:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/tickets/${id}/messages`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setMessages(data);
      }
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim()) return;

    setSendingMessage(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/tickets/${id}/messages`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          message: newMessage,
          is_internal: false
        })
      });

      if (response.ok) {
        setNewMessage('');
        fetchMessages();
        fetchTicketDetail(); // Refresh to update message count
      }
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Failed to send message');
    } finally {
      setSendingMessage(false);
    }
  };

  const handleSignature = async (signatureData) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/tickets/${id}/signature`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          signature_data: signatureData,
          signature_type: 'approval'
        })
      });

      if (response.ok) {
        alert('✅ Signature submitted successfully! Ticket has been closed.');
        setShowSignaturePad(false);
        fetchTicketDetail();
      } else {
        alert('Failed to submit signature');
      }
    } catch (error) {
      console.error('Error submitting signature:', error);
      alert('Failed to submit signature');
    }
  };

  const getStatusBadge = (status) => {
    const badges = {
      'open': { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Open' },
      'in_progress': { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'In Progress' },
      'resolved': { bg: 'bg-green-100', text: 'text-green-800', label: 'Resolved' },
      'approve': { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Awaiting Approval' },
      'closed': { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Closed' }
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

  if (loading) {
    return (
      <Layout>
        <div className="p-6 flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading ticket...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (!ticket) {
    return (
      <Layout>
        <div className="p-6 text-center">
          <p className="text-gray-600">Ticket not found</p>
        </div>
      </Layout>
    );
  }

  const statusBadge = getStatusBadge(ticket.status);
  const priorityBadge = getPriorityBadge(ticket.priority);

  return (
    <Layout>
      <div className="p-6 max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={() => navigate('/tickets')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-6 h-6 text-gray-600" />
          </button>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-2xl font-bold text-gray-900">
                Ticket #{ticket.ticket_number}
              </h1>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${statusBadge.bg} ${statusBadge.text}`}>
                {statusBadge.label}
              </span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${priorityBadge.bg} ${priorityBadge.text}`}>
                {priorityBadge.label}
              </span>
            </div>
            <p className="text-gray-600">{ticket.subject}</p>
          </div>
        </div>

        {/* Status Timeline */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Ticket Progress</h2>
          <TicketStatusTimeline currentStatus={ticket.status} />
        </div>

        {/* Approval Required Alert */}
        {ticket.status === 'approve' && !ticket.signature_id && (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4 mb-6 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-orange-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-medium text-orange-900">Approval Required</p>
              <p className="text-xs text-orange-700 mt-1">
                This ticket has been resolved and requires your approval. Please review the solution and provide your digital signature to close the ticket.
              </p>
              <button
                onClick={() => setShowSignaturePad(true)}
                className="mt-3 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors text-sm font-medium"
              >
                Approve & Sign
              </button>
            </div>
          </div>
        )}

        {/* Signature Pad Modal */}
        {showSignaturePad && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-6 max-w-2xl w-full">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Approve Ticket Resolution</h3>
              <SignaturePad
                onSave={handleSignature}
                onCancel={() => setShowSignaturePad(false)}
              />
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Ticket Details */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Description</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{ticket.description}</p>

              {/* Attachments */}
              {ticket.attachments && ticket.attachments.length > 0 && (
                <div className="mt-6">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">Attachments</h3>
                  <div className="grid grid-cols-2 gap-3">
                    {ticket.attachments.map((attachment, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-3 flex items-center gap-3 hover:bg-gray-50">
                        {attachment.file_type?.includes('image') ? (
                          <ImageIcon className="w-8 h-8 text-blue-500" />
                        ) : (
                          <FileText className="w-8 h-8 text-red-500" />
                        )}
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-gray-900 truncate">
                            {attachment.file_name}
                          </p>
                          <div className="flex items-center gap-2 mt-1">
                            {attachment.gps_coordinates && (
                              <span className="text-xs text-green-600 flex items-center gap-1">
                                <MapPin className="w-3 h-3" />
                                GPS
                              </span>
                            )}
                            {attachment.timestamp_metadata && (
                              <span className="text-xs text-blue-600 flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {new Date(attachment.timestamp_metadata).toLocaleString()}
                              </span>
                            )}
                          </div>
                        </div>
                        <button className="p-1 hover:bg-blue-50 rounded">
                          <Download className="w-4 h-4 text-blue-600" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Messages */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Conversation ({messages.length})
              </h2>

              <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
                {messages.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No messages yet</p>
                ) : (
                  messages.map((message) => (
                    <div key={message.id} className="flex gap-3">
                      <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                        <User className="w-5 h-5 text-blue-600" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-gray-900">
                            {message.user_name}
                          </span>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            message.user_role === 'admin' ? 'bg-purple-100 text-purple-700' :
                            message.user_role === 'technician' ? 'bg-green-100 text-green-700' :
                            'bg-blue-100 text-blue-700'
                          }`}>
                            {message.user_role}
                          </span>
                          <span className="text-xs text-gray-500">
                            {new Date(message.created_at).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-gray-700 bg-gray-50 rounded-lg p-3">
                          {message.message}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* New Message */}
              {ticket.status !== 'closed' && (
                <form onSubmit={handleSendMessage}>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      placeholder="Type your message..."
                      className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      disabled={sendingMessage}
                    />
                    <button
                      type="submit"
                      disabled={sendingMessage || !newMessage.trim()}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      <Send className="w-5 h-5" />
                      Send
                    </button>
                  </div>
                </form>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Ticket Info */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Ticket Information</h3>
              <div className="space-y-3 text-sm">
                <div>
                  <p className="text-gray-600">Category</p>
                  <p className="font-medium text-gray-900 flex items-center gap-2 mt-1">
                    <Tag className="w-4 h-4" />
                    {getCategoryLabel(ticket.category)}
                  </p>
                </div>
                <div>
                  <p className="text-gray-600">Created</p>
                  <p className="font-medium text-gray-900 flex items-center gap-2 mt-1">
                    <Clock className="w-4 h-4" />
                    {new Date(ticket.created_at).toLocaleString()}
                  </p>
                </div>
                {ticket.assigned_to_name && (
                  <div>
                    <p className="text-gray-600">Assigned To</p>
                    <p className="font-medium text-gray-900 flex items-center gap-2 mt-1">
                      <User className="w-4 h-4" />
                      {ticket.assigned_to_name}
                    </p>
                  </div>
                )}
                {ticket.resolved_at && (
                  <div>
                    <p className="text-gray-600">Resolved At</p>
                    <p className="font-medium text-gray-900 flex items-center gap-2 mt-1">
                      <Clock className="w-4 h-4" />
                      {new Date(ticket.resolved_at).toLocaleString()}
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default TicketDetail;
