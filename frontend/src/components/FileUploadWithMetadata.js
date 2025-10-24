import React, { useState, useEffect } from 'react';
import { Upload, MapPin, Clock, X, FileText, Image as ImageIcon } from 'lucide-react';

const FileUploadWithMetadata = ({ onFileSelect, maxFiles = 5, acceptedTypes = 'image/*,application/pdf' }) => {
  const [files, setFiles] = useState([]);
  const [gpsCoords, setGpsCoords] = useState(null);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [gpsError, setGpsError] = useState(null);

  // Get GPS coordinates automatically
  useEffect(() => {
    if (navigator.geolocation) {
      setGpsLoading(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const coords = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          };
          setGpsCoords(coords);
          setGpsLoading(false);
        },
        (error) => {
          console.error('GPS Error:', error);
          setGpsError(error.message);
          setGpsLoading(false);
        },
        { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
      );
    }
  }, []);

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    
    if (files.length + selectedFiles.length > maxFiles) {
      alert(`Maximum ${maxFiles} files allowed`);
      return;
    }

    const newFiles = selectedFiles.map(file => ({
      file,
      preview: file.type.startsWith('image/') ? URL.createObjectURL(file) : null,
      timestamp: new Date().toISOString(),
      gpsCoords: gpsCoords
    }));

    const updatedFiles = [...files, ...newFiles];
    setFiles(updatedFiles);
    onFileSelect(updatedFiles);
  };

  const removeFile = (index) => {
    const updatedFiles = files.filter((_, i) => i !== index);
    setFiles(updatedFiles);
    onFileSelect(updatedFiles);
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  return (
    <div className="space-y-4">
      {/* GPS Status */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
        <div className="flex items-start gap-2">
          <MapPin className="w-5 h-5 text-blue-600 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-blue-900">GPS Location</p>
            {gpsLoading && (
              <p className="text-xs text-blue-600">Getting location...</p>
            )}
            {gpsError && (
              <p className="text-xs text-red-600">GPS unavailable: {gpsError}</p>
            )}
            {gpsCoords && (
              <p className="text-xs text-blue-700">
                📍 {gpsCoords.latitude.toFixed(6)}, {gpsCoords.longitude.toFixed(6)}
                {gpsCoords.accuracy && ` (±${Math.round(gpsCoords.accuracy)}m)`}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Upload Area */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition-colors">
        <input
          type="file"
          id="file-upload"
          multiple
          accept={acceptedTypes}
          onChange={handleFileChange}
          className="hidden"
        />
        <label htmlFor="file-upload" className="cursor-pointer">
          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
          <p className="text-sm font-medium text-gray-700">Click to upload files</p>
          <p className="text-xs text-gray-500 mt-1">Images or PDF (max {maxFiles} files)</p>
        </label>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-gray-700">Uploaded Files ({files.length}/{maxFiles})</p>
          {files.map((fileData, index) => (
            <div key={index} className="bg-white border border-gray-200 rounded-lg p-3 flex items-center gap-3">
              {/* Preview or Icon */}
              {fileData.preview ? (
                <img src={fileData.preview} alt="Preview" className="w-12 h-12 object-cover rounded" />
              ) : (
                <div className="w-12 h-12 bg-gray-100 rounded flex items-center justify-center">
                  {fileData.file.type.includes('pdf') ? (
                    <FileText className="w-6 h-6 text-red-500" />
                  ) : (
                    <ImageIcon className="w-6 h-6 text-gray-400" />
                  )}
                </div>
              )}

              {/* File Info */}
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {fileData.file.name}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(fileData.file.size)}
                </p>
                <div className="flex items-center gap-3 mt-1">
                  {fileData.gpsCoords && (
                    <span className="text-xs text-green-600 flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      GPS
                    </span>
                  )}
                  <span className="text-xs text-blue-600 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {new Date(fileData.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>

              {/* Remove Button */}
              <button
                onClick={() => removeFile(index)}
                className="p-1 hover:bg-red-50 rounded-full transition-colors"
              >
                <X className="w-5 h-5 text-red-500" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileUploadWithMetadata;