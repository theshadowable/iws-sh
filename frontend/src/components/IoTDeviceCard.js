import React from 'react';
import { Activity, Droplets, Battery, Wifi, ThermometerSun, Gauge, Edit2, Trash2 } from 'lucide-react';

const IoTDeviceCard = ({ device, metrics, onClick, onEdit, onDelete }) => {
  const getStatusColor = (status) => {
    switch (status) {
      case 'online': return 'bg-green-500';
      case 'offline': return 'bg-gray-400';
      case 'error': return 'bg-red-500';
      case 'warning': return 'bg-yellow-500';
      default: return 'bg-gray-400';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'online': return 'Online';
      case 'offline': return 'Offline';
      case 'error': return 'Error';
      case 'warning': return 'Warning';
      default: return 'Unknown';
    }
  };

  const getBatteryColor = (level) => {
    if (level > 50) return 'text-green-600';
    if (level > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getSignalColor = (strength) => {
    if (!strength) return 'text-gray-400';
    if (strength > -50) return 'text-green-600';
    if (strength > -70) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div 
      onClick={onClick}
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow cursor-pointer border border-gray-200"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">
            {metrics?.device_name || device?.device_name || 'Unknown Device'}
          </h3>
          <p className="text-sm text-gray-500">
            {device?.device_id}
          </p>
        </div>
        <div className="flex flex-col items-end">
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full ${getStatusColor(metrics?.status || device?.status)} bg-opacity-10`}>
            <div className={`w-2 h-2 rounded-full ${getStatusColor(metrics?.status || device?.status)}`}></div>
            <span className={`text-sm font-medium ${getStatusColor(metrics?.status || device?.status)} bg-opacity-100`}>
              {getStatusText(metrics?.status || device?.status)}
            </span>
          </div>
        </div>
      </div>

      {/* Current Flow Rate */}
      <div className="mb-4 p-4 bg-blue-50 rounded-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Droplets className="w-5 h-5 text-blue-600" />
            <span className="text-sm text-gray-600">Flow Rate</span>
          </div>
          <span className="text-2xl font-bold text-blue-600">
            {metrics?.current_flow_rate?.toFixed(2) || '0.00'}
            <span className="text-sm ml-1">L/min</span>
          </span>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-3 mb-4">
        {/* Temperature */}
        {metrics?.current_temperature !== null && metrics?.current_temperature !== undefined && (
          <div className="flex items-center gap-2 p-2 bg-gray-50 rounded">
            <ThermometerSun className="w-4 h-4 text-orange-600" />
            <div>
              <p className="text-xs text-gray-500">Temp</p>
              <p className="text-sm font-semibold">{metrics.current_temperature?.toFixed(1)}°C</p>
            </div>
          </div>
        )}

        {/* Pressure */}
        {metrics?.current_pressure !== null && metrics?.current_pressure !== undefined && (
          <div className="flex items-center gap-2 p-2 bg-gray-50 rounded">
            <Gauge className="w-4 h-4 text-purple-600" />
            <div>
              <p className="text-xs text-gray-500">Pressure</p>
              <p className="text-sm font-semibold">{metrics.current_pressure?.toFixed(2)} Bar</p>
            </div>
          </div>
        )}

        {/* Battery */}
        {metrics?.battery_level !== null && metrics?.battery_level !== undefined && (
          <div className="flex items-center gap-2 p-2 bg-gray-50 rounded">
            <Battery className={`w-4 h-4 ${getBatteryColor(metrics.battery_level)}`} />
            <div>
              <p className="text-xs text-gray-500">Battery</p>
              <p className={`text-sm font-semibold ${getBatteryColor(metrics.battery_level)}`}>
                {metrics.battery_level}%
              </p>
            </div>
          </div>
        )}

        {/* Signal */}
        {metrics?.signal_strength !== null && metrics?.signal_strength !== undefined && (
          <div className="flex items-center gap-2 p-2 bg-gray-50 rounded">
            <Wifi className={`w-4 h-4 ${getSignalColor(metrics.signal_strength)}`} />
            <div>
              <p className="text-xs text-gray-500">Signal</p>
              <p className={`text-sm font-semibold ${getSignalColor(metrics.signal_strength)}`}>
                {metrics.signal_strength} dBm
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Today's Stats */}
      <div className="pt-3 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Today's Volume:</span>
          <span className="font-semibold">{(metrics?.today_volume || 0).toFixed(2)} L</span>
        </div>
        <div className="flex items-center justify-between text-sm mt-1">
          <span className="text-gray-600">Today's Cost:</span>
          <span className="font-semibold text-green-600">Rp {(metrics?.today_cost || 0).toLocaleString('id-ID')}</span>
        </div>
      </div>

      {/* Last Update */}
      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <Activity className="w-3 h-3" />
            <span>
              Last update: {metrics?.last_updated ? new Date(metrics.last_updated).toLocaleTimeString() : 'Never'}
            </span>
          </div>
          {(onEdit || onDelete) && (
            <div className="flex items-center gap-2">
              {onEdit && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onEdit(device);
                  }}
                  className="p-1 text-blue-600 hover:bg-blue-50 rounded transition-colors"
                  title="Edit Device"
                >
                  <Edit2 className="w-4 h-4" />
                </button>
              )}
              {onDelete && (
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(device);
                  }}
                  className="p-1 text-red-600 hover:bg-red-50 rounded transition-colors"
                  title="Delete Device"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IoTDeviceCard;
