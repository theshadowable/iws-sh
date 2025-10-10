import React, { useState, useRef } from 'react';
import axios from 'axios';
import { Camera, Upload, X, Loader, CheckCircle, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const PhotoUpload = ({ onPhotoUploaded, onOCRResult, token }) => {
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [preview, setPreview] = useState(null);
  const [ocrResult, setOcrResult] = useState(null);
  const fileInputRef = useRef(null);
  const cameraInputRef = useRef(null);

  const handleFileSelect = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Show preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result);
    };
    reader.readAsDataURL(file);

    // Upload file
    await uploadFile(file);
  };

  const uploadFile = async (file) => {
    try {
      setUploading(true);
      setOcrResult(null);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('process_ocr', 'true');

      const response = await axios.post(
        `${BACKEND_URL}/api/upload/meter-photo`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      const data = response.data;
      
      // Notify parent component
      if (onPhotoUploaded) {
        onPhotoUploaded(data.file_path);
      }

      // Process OCR result
      if (data.ocr) {
        setOcrResult(data.ocr);
        if (data.ocr.success && onOCRResult) {
          onOCRResult(data.ocr.reading_value, data.ocr.confidence);
        }
      }

      toast.success('Photo uploaded successfully!');
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error(error.response?.data?.detail || 'Failed to upload photo');
    } finally {
      setUploading(false);
    }
  };

  const clearPhoto = () => {
    setPreview(null);
    setOcrResult(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  return (
    <div className="space-y-4">
      {/* Upload Buttons */}
      {!preview && (
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="flex-1 px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors flex items-center justify-center gap-2 text-gray-700"
          >
            <Upload className="h-5 w-5" />
            <span>Choose Photo</span>
          </button>

          <button
            type="button"
            onClick={() => cameraInputRef.current?.click()}
            className="flex-1 px-4 py-3 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors flex items-center justify-center gap-2 text-gray-700"
          >
            <Camera className="h-5 w-5" />
            <span>Take Photo</span>
          </button>
        </div>
      )}

      {/* Hidden file inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        onChange={handleFileSelect}
        className="hidden"
      />

      {/* Preview and OCR Result */}
      {preview && (
        <div className="border-2 border-gray-200 rounded-lg p-4 space-y-4">
          <div className="flex items-start justify-between">
            <h4 className="font-medium text-gray-900">Uploaded Photo</h4>
            <button
              type="button"
              onClick={clearPhoto}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Image Preview */}
          <div className="relative">
            <img
              src={preview}
              alt="Meter preview"
              className="w-full h-64 object-cover rounded-lg"
            />
            {uploading && (
              <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center rounded-lg">
                <Loader className="h-8 w-8 text-white animate-spin" />
              </div>
            )}
          </div>

          {/* OCR Result */}
          {ocrResult && (
            <div className={`p-4 rounded-lg ${
              ocrResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
            }`}>
              {ocrResult.success ? (
                <>
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <span className="font-semibold text-green-900">OCR Processing Complete</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-green-700">Extracted Reading:</span>
                      <span className="font-bold text-green-900">{ocrResult.reading_value} m³</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-green-700">Confidence:</span>
                      <span className="font-semibold text-green-900">{ocrResult.confidence}%</span>
                    </div>
                    {ocrResult.all_numbers && ocrResult.all_numbers.length > 1 && (
                      <div className="mt-2 pt-2 border-t border-green-200">
                        <span className="text-xs text-green-600">Other detected numbers: {ocrResult.all_numbers.join(', ')}</span>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <div className="flex items-center gap-2 mb-2">
                    <AlertCircle className="h-5 w-5 text-red-600" />
                    <span className="font-semibold text-red-900">OCR Processing Failed</span>
                  </div>
                  <p className="text-sm text-red-700">{ocrResult.error || 'Could not extract reading from image'}</p>
                  <p className="text-xs text-red-600 mt-2">Please enter the reading manually or try taking another photo.</p>
                </>
              )}
            </div>
          )}
        </div>
      )}

      {/* Instructions */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <h4 className="text-sm font-semibold text-blue-900 mb-1">Photo Tips for Best OCR Results:</h4>
        <ul className="text-xs text-blue-800 space-y-1 list-disc list-inside">
          <li>Ensure good lighting on the meter display</li>
          <li>Keep the camera steady and focused</li>
          <li>Capture only the meter reading display</li>
          <li>Avoid shadows and reflections</li>
        </ul>
      </div>
    </div>
  );
};