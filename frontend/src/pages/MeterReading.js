import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { PhotoUpload } from '@/components/PhotoUpload';
import { QRScanner } from '@/components/QRScanner';
import axios from 'axios';
import { Camera, Save, X, MapPin, Droplets, QrCode } from 'lucide-react';
import { toast } from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const MeterReading = () => {
  const { token, user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [devices, setDevices] = useState([]);
  const [customers, setCustomers] = useState([]);
  
  const [formData, setFormData] = useState({
    device_id: '',
    reading_value: '',
    reading_method: 'manual',
    notes: '',
    location_lat: null,
    location_lng: null,
    photo_path: null
  });

  const [showQRScanner, setShowQRScanner] = useState(false);
  const [showPhotoUpload, setShowPhotoUpload] = useState(false);

  useEffect(() => {
    fetchDevices();
    fetchCustomers();
    getCurrentLocation();
  }, []);

  const fetchDevices = async () => {
    try {
      const response = await axios.get(`${API}/devices`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDevices(response.data);
    } catch (error) {
      console.error('Failed to fetch devices:', error);
    }
  };

  const fetchCustomers = async () => {
    try {
      const response = await axios.get(`${API}/customers`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCustomers(response.data);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    }
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData(prev => ({
            ...prev,
            location_lat: position.coords.latitude,
            location_lng: position.coords.longitude
          }));
        },
        (error) => {
          console.error('Error getting location:', error);
        }
      );
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.device_id || !formData.reading_value) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      setLoading(true);
      
      await axios.post(
        `${API}/technician/meter-readings`,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('Meter reading submitted successfully!');
      
      // Reset form
      setFormData({
        device_id: '',
        reading_value: '',
        reading_method: 'manual',
        notes: '',
        location_lat: formData.location_lat,
        location_lng: formData.location_lng
      });
    } catch (error) {
      console.error('Failed to submit reading:', error);
      toast.error(error.response?.data?.detail || 'Failed to submit meter reading');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handlePhotoUploaded = (filePath) => {
    setFormData(prev => ({
      ...prev,
      photo_path: filePath,
      reading_method: 'photo'
    }));
  };

  const handleOCRResult = (readingValue, confidence) => {
    setFormData(prev => ({
      ...prev,
      reading_value: readingValue.toString(),
      reading_method: 'ocr'
    }));
    toast.success(`OCR detected reading: ${readingValue} m³ (${confidence}% confidence)`);
  };

  const handleQRScanSuccess = (scanData) => {
    if (scanData.type === 'device') {
      setFormData(prev => ({
        ...prev,
        device_id: scanData.data.id
      }));
      toast.success(`Device selected: ${scanData.data.device_name}`);
    }
    setShowQRScanner(false);
  };

  return (
    <Layout>
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Submit Meter Reading</h1>
          <p className="text-gray-600 mt-1">Record water meter readings</p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Device Selection */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Select Meter/Device *
                </label>
                <button
                  type="button"
                  onClick={() => setShowQRScanner(!showQRScanner)}
                  className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  <QrCode className="h-4 w-4" />
                  <span>Scan QR/Barcode</span>
                </button>
              </div>
              
              {showQRScanner ? (
                <QRScanner
                  token={token}
                  onScanSuccess={handleQRScanSuccess}
                  onClose={() => setShowQRScanner(false)}
                />
              ) : (
                <select
                  name="device_id"
                  value={formData.device_id}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Choose a device...</option>
                  {devices.map(device => (
                    <option key={device.id} value={device.id}>
                      {device.device_name} - {device.device_id}
                    </option>
                  ))}
                </select>
              )}
            </div>

            {/* Photo Upload with OCR */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-gray-700">
                  Meter Photo (Optional)
                </label>
                <button
                  type="button"
                  onClick={() => setShowPhotoUpload(!showPhotoUpload)}
                  className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
                >
                  <Camera className="h-4 w-4" />
                  <span>{showPhotoUpload ? 'Hide' : 'Show'} Photo Upload</span>
                </button>
              </div>
              
              {showPhotoUpload && (
                <PhotoUpload
                  token={token}
                  onPhotoUploaded={handlePhotoUploaded}
                  onOCRResult={handleOCRResult}
                />
              )}
            </div>

            {/* Reading Value */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Meter Reading Value * (m³)
              </label>
              <div className="relative">
                <Droplets className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type="number"
                  step="0.001"
                  name="reading_value"
                  value={formData.reading_value}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter reading value or use OCR"
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Enter manually or use photo OCR above to auto-detect
              </p>
            </div>

            {/* Reading Method */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Reading Method
              </label>
              <select
                name="reading_method"
                value={formData.reading_method}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="manual">Manual Entry</option>
                <option value="photo">Photo (OCR Pending)</option>
                <option value="barcode">Barcode Scanner</option>
                <option value="qr_code">QR Code Scanner</option>
              </select>
            </div>

            {/* Location */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location
              </label>
              <div className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 px-4 py-3 rounded-lg">
                <MapPin className="h-4 w-4" />
                {formData.location_lat && formData.location_lng ? (
                  <span>
                    Lat: {formData.location_lat.toFixed(6)}, Lng: {formData.location_lng.toFixed(6)}
                  </span>
                ) : (
                  <span>Location not available</span>
                )}
              </div>
            </div>

            {/* Notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Notes (Optional)
              </label>
              <textarea
                name="notes"
                value={formData.notes}
                onChange={handleInputChange}
                rows={3}
                placeholder="Add any observations or notes..."
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              />
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 pt-4">
              <button
                type="submit"
                disabled={loading}
                className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:bg-blue-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    Submitting...
                  </>
                ) : (
                  <>
                    <Save className="h-5 w-5" />
                    Submit Reading
                  </>
                )}
              </button>
              
              <button
                type="button"
                onClick={() => window.history.back()}
                className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>

        {/* Info Box */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-blue-900 mb-2">Tips for Accurate Readings</h3>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>Ensure you can clearly see the meter display</li>
            <li>Record all digits shown on the meter</li>
            <li>Take note of any unusual observations</li>
            <li>Verify the reading before submission</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
};