import React from 'react';
import { CheckCircle, Circle, Clock, AlertCircle, XCircle } from 'lucide-react';

const TicketStatusTimeline = ({ currentStatus }) => {
  const statuses = [
    { key: 'open', label: 'Open', icon: Circle, color: 'blue' },
    { key: 'in_progress', label: 'In Progress', icon: Clock, color: 'yellow' },
    { key: 'resolved', label: 'Resolved', icon: CheckCircle, color: 'green' },
    { key: 'approve', label: 'Approve', icon: AlertCircle, color: 'orange' },
    { key: 'closed', label: 'Closed', icon: CheckCircle, color: 'gray' }
  ];

  const currentIndex = statuses.findIndex(s => s.key === currentStatus);

  const getStatusColor = (status, index) => {
    if (index <= currentIndex) {
      // Active or completed
      switch (status.color) {
        case 'blue': return 'bg-blue-600 text-white';
        case 'yellow': return 'bg-yellow-500 text-white';
        case 'green': return 'bg-green-600 text-white';
        case 'orange': return 'bg-orange-500 text-white';
        case 'gray': return 'bg-gray-600 text-white';
        default: return 'bg-gray-600 text-white';
      }
    }
    // Inactive
    return 'bg-gray-200 text-gray-400';
  };

  const getLineColor = (index) => {
    if (index < currentIndex) {
      return 'bg-green-600';
    }
    return 'bg-gray-300';
  };

  return (
    <div className="py-4">
      <div className="flex items-center justify-between relative">
        {statuses.map((status, index) => {
          const Icon = status.icon;
          const isActive = index <= currentIndex;
          const isCurrent = index === currentIndex;

          return (
            <React.Fragment key={status.key}>
              {/* Status Item */}
              <div className="flex flex-col items-center relative z-10">
                <div
                  className={`w-12 h-12 rounded-full flex items-center justify-center transition-all ${
                    getStatusColor(status, index)
                  } ${
                    isCurrent ? 'ring-4 ring-blue-200 scale-110' : ''
                  }`}
                >
                  <Icon className="w-6 h-6" />
                </div>
                <p className={`text-xs mt-2 font-medium ${
                  isActive ? 'text-gray-900' : 'text-gray-400'
                }`}>
                  {status.label}
                </p>
              </div>

              {/* Connector Line */}
              {index < statuses.length - 1 && (
                <div className="flex-1 h-1 mx-2 relative">
                  <div className="absolute top-0 left-0 right-0 h-full bg-gray-300 rounded"></div>
                  <div
                    className={`absolute top-0 left-0 h-full rounded transition-all duration-500 ${
                      getLineColor(index)
                    }`}
                    style={{ width: index < currentIndex ? '100%' : '0%' }}
                  ></div>
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
};

export default TicketStatusTimeline;