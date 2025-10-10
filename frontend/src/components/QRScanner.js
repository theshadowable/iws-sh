import React, { useState, useEffect } from 'react';
import { Html5QrcodeScanner } from 'html5-qrcode';
import { QrCode, X } from 'lucide-react';
import axios from 'axios';
import { toast } from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

export const QRScanner = ({ onScanSuccess, token, onClose }) => {
  const [scanning, setScanning] = useState(false);
  const [scanner, setScanner] = useState(null);

  useEffect(() => {
    if (scanning) {
      const html5QrcodeScanner = new Html5QrcodeScanner(
        "qr-reader",
        { 
          fps: 10, 
          qrbox: { width: 250, height: 250 },
          aspectRatio: 1.0
        },
        false
      );

      html5QrcodeScanner.render(onScanSuccess, onScanFailure);
      setScanner(html5QrcodeScanner);

      return () => {
        html5QrcodeScanner.clear().catch(error => {
          console.error("Failed to clear scanner:", error);
        });
      };
    }
  }, [scanning]);

  const handleScan = async (decodedText, decodedResult) => {
    try {
      // Stop scanner
      if (scanner) {
        await scanner.clear();
      }
      setScanning(false);

      // Process barcode/QR data
      const formData = new FormData();
      formData.append('barcode_data', decodedText);

      const response = await axios.post(
        `${BACKEND_URL}/api/upload/barcode-scan`,
        formData,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'multipart/form-data'
          }
        }
      );

      if (response.data.success) {
        toast.success(`${response.data.type} found!`);
        if (onScanSuccess) {
          onScanSuccess(response.data);
        }
      } else {
        toast.error('No matching device or customer found');
      }
    } catch (error) {
      console.error('Scan processing failed:', error);
      toast.error('Failed to process scanned code');
    }
  };

  const onScanFailure = (error) => {
    // Ignore common scanning errors
    if (error && !error.includes('NotFoundException')) {
      console.warn('QR Scan error:', error);
    }
  };

  const startScanning = () => {
    setScanning(true);
  };

  const stopScanning = async () => {
    if (scanner) {
      await scanner.clear();
    }
    setScanning(false);
    if (onClose) {
      onClose();
    }
  };

  return (
    <div className="space-y-4">
      {!scanning ? (
        <button
          type="button"
          onClick={startScanning}
          className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center justify-center gap-2"
        >
          <QrCode className="h-5 w-5" />
          <span>Scan QR/Barcode</span>
        </button>
      ) : (
        <div className="border-2 border-blue-200 rounded-lg p-4 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-gray-900">Scanning...</h4>
            <button
              type="button"
              onClick={stopScanning}
              className="text-gray-400 hover:text-gray-600"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          
          {/* QR Scanner Container */}
          <div id="qr-reader" className="w-full"></div>

          <div className="bg-blue-50 border border-blue-200 rounded p-3">
            <p className="text-sm text-blue-800">
              Point your camera at the QR code or barcode on the meter or customer card.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};