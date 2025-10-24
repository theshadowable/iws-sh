import React, { useState } from 'react';
import { ArrowLeft, Send, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import FileUploadWithMetadata from '../components/FileUploadWithMetadata';

const CreateTicket = () => {
  const [formData, setFormData] = useState({
    category: 'technical_issue',
    priority: 'medium',
    subject: '',
    description: ''
  });
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const token = localStorage.getItem('token');

      // Get GPS coordinates from first file if available
      let gpsCoordinates = null;
      if (files.length > 0 && files[0].gpsCoords) {
        gpsCoordinates = files[0].gpsCoords;
      }

      // Create ticket first
      const ticketResponse = await fetch(`${BACKEND_URL}/api/tickets`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...formData,
          gps_coordinates: gpsCoordinates
        })
      });

      if (!ticketResponse.ok) {
        throw new Error('Failed to create ticket');
      }

      const ticket = await ticketResponse.json();

      // Upload attachments if any
      if (files.length > 0) {
        for (const fileData of files) {
          const formDataUpload = new FormData();
          formDataUpload.append('file', fileData.file);
          
          if (fileData.gpsCoords) {
            formDataUpload.append('gps_latitude', fileData.gpsCoords.latitude);
            formDataUpload.append('gps_longitude', fileData.gpsCoords.longitude);
            if (fileData.gpsCoords.accuracy) {
              formDataUpload.append('gps_accuracy', fileData.gpsCoords.accuracy);
            }
          }

          await fetch(`${BACKEND_URL}/api/tickets/${ticket.id}/attachments`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`
            },
            body: formDataUpload
          });
        }
      }

      // Navigate to ticket detail
      navigate(`/tickets/${ticket.id}`);
    } catch (err) {
      console.error('Error creating ticket:', err);
      setError('Failed to create ticket. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="p-6 max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={() => navigate('/tickets')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-6 h-6 text-gray-600" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Support Ticket</h1>
            <p className="text-gray-600 mt-1">Submit a new support request</p>
          </div>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm font-medium text-blue-900">Important Information</p>
            <p className="text-xs text-blue-700 mt-1">
              Your location and timestamp will be automatically captured with file uploads for faster support processing.
              Please provide as much detail as possible to help us resolve your issue quickly.
            </p>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Category */}
          <div className="bg-white rounded-lg shadow p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category *
            </label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="technical_issue">Technical Issue</option>
              <option value="water_quality">Water Quality</option>
              <option value="maintenance_repairs">Maintenance & Repairs</option>
              <option value="general_inquiry">General Inquiry</option>
            </select>
          </div>

          {/* Priority */}
          <div className="bg-white rounded-lg shadow p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Priority *
            </label>
            <select
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            >
              <option value="low">Low - Can wait a few days</option>
              <option value="medium">Medium - Within 1-2 days</option>
              <option value="high">High - Urgent, within 24 hours</option>
              <option value="critical">Critical - Emergency, immediate attention</option>
            </select>
          </div>

          {/* Subject */}
          <div className="bg-white rounded-lg shadow p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Subject *
            </label>
            <input
              type="text"
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
              placeholder="Brief summary of your issue"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
              minLength={5}
              maxLength={200}
            />
            <p className="text-xs text-gray-500 mt-1">
              {formData.subject.length}/200 characters
            </p>
          </div>

          {/* Description */}
          <div className="bg-white rounded-lg shadow p-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Detailed description of your issue. Please include any error messages, steps to reproduce, or relevant information."
              rows={6}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
              minLength={10}
              maxLength={2000}
            />
            <p className="text-xs text-gray-500 mt-1">
              {formData.description.length}/2000 characters
            </p>
          </div>

          {/* File Upload */}
          <div className="bg-white rounded-lg shadow p-6">
            <label className="block text-sm font-medium text-gray-700 mb-4">
              Attachments (Optional)
            </label>
            <FileUploadWithMetadata
              onFileSelect={setFiles}
              maxFiles={5}
              acceptedTypes="image/*,application/pdf"
            />
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => navigate('/tickets')}
              className="flex-1 px-6 py-3 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  Creating...
                </>
              ) : (
                <>
                  <Send className="w-5 h-5" />
                  Submit Ticket
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
};

export default CreateTicket;
