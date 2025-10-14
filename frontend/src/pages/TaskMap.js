import React, { useState, useEffect } from 'react';
import { Layout } from '@/components/Layout';
import { useAuth } from '@/contexts/AuthContext';
import { MapView } from '@/components/MapView';
import axios from 'axios';
import { MapPin, Navigation, Clock, CheckCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export const TaskMap = () => {
  const { token, user } = useAuth();
  const [tasks, setTasks] = useState([]);
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentLocation, setCurrentLocation] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch tasks assigned to current technician
      const tasksResponse = await axios.get(
        `${API}/technician/work-orders?assigned_to=${user.id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTasks(tasksResponse.data);

      // Fetch properties
      const propsResponse = await axios.get(
        `${API}/properties`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setProperties(propsResponse.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      toast.error('Failed to load map data', { id: 'map-data-error' });
    } finally {
      setLoading(false);
    }
  };

  const handleLocationUpdate = (location) => {
    setCurrentLocation(location);
    // Here you could also send location to backend for tracking
    // updateTechnicianLocation(location);
  };

  // Prepare locations for map
  const mapLocations = tasks
    .filter(task => task.location_lat && task.location_lng)
    .map(task => ({
      lat: task.location_lat,
      lng: task.location_lng,
      label: task.title,
      address: task.location_address,
      type: 'task',
      taskData: task
    }));

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Task Map & Navigation</h1>
          <p className="text-gray-600 mt-1">View and navigate to your assigned tasks</p>
        </div>

        {/* Current Location Card */}
        {currentLocation && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-center gap-3">
              <MapPin className="h-6 w-6 text-blue-600" />
              <div>
                <h3 className="font-semibold text-blue-900">Your Current Location</h3>
                <p className="text-sm text-blue-700">
                  Lat: {currentLocation.lat.toFixed(6)}, Lng: {currentLocation.lng.toFixed(6)}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Map */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Task Locations</h2>
          <MapView
            center={currentLocation ? [currentLocation.lat, currentLocation.lng] : [-6.2088, 106.8456]}
            zoom={12}
            locations={mapLocations}
            currentLocation={currentLocation}
            onLocationUpdate={handleLocationUpdate}
            height="500px"
          />
        </div>

        {/* Task List */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Your Tasks</h2>
          
          {tasks.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <MapPin className="h-12 w-12 mx-auto mb-2 text-gray-400" />
              <p>No tasks assigned</p>
            </div>
          ) : (
            <div className="space-y-3">
              {tasks.map((task) => (
                <div
                  key={task.id}
                  className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{task.title}</h3>
                      <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                      
                      {task.location_address && (
                        <div className="flex items-center gap-2 mt-2 text-sm text-gray-500">
                          <MapPin className="h-4 w-4" />
                          <span>{task.location_address}</span>
                        </div>
                      )}

                      <div className="flex items-center gap-4 mt-2">
                        {task.scheduled_date && (
                          <div className="flex items-center gap-1 text-xs text-gray-500">
                            <Clock className="h-3 w-3" />
                            <span>{new Date(task.scheduled_date).toLocaleDateString()}</span>
                          </div>
                        )}
                        
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          task.status === 'completed' ? 'bg-green-100 text-green-800' :
                          task.status === 'in_progress' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {task.status.replace('_', ' ')}
                        </span>
                      </div>
                    </div>

                    {task.location_lat && task.location_lng && (
                      <button
                        onClick={() => {
                          const url = currentLocation
                            ? `https://www.google.com/maps/dir/?api=1&origin=${currentLocation.lat},${currentLocation.lng}&destination=${task.location_lat},${task.location_lng}&travelmode=driving`
                            : `https://www.google.com/maps?q=${task.location_lat},${task.location_lng}`;
                          window.open(url, '_blank');
                        }}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium flex items-center gap-2 whitespace-nowrap"
                      >
                        <Navigation className="h-4 w-4" />
                        <span>Navigate</span>
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Info Box */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-green-900 mb-2">Navigation Tips</h3>
          <ul className="text-sm text-green-800 space-y-1 list-disc list-inside">
            <li>Click on map markers to see task details and get directions</li>
            <li>Your location is shown with a blue marker</li>
            <li>Task locations are shown with red markers</li>
            <li>Click "Navigate" to open Google Maps for turn-by-turn directions</li>
          </ul>
        </div>
      </div>
    </Layout>
  );
};