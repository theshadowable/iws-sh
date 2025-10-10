import os
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Tuple
import pytesseract
from PIL import Image
import re


# File upload configuration
UPLOAD_DIR = Path("/app/backend/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

METER_PHOTOS_DIR = UPLOAD_DIR / "meter_photos"
METER_PHOTOS_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def save_uploaded_file(file_content: bytes, filename: str, subfolder: str = "meter_photos") -> str:
    """Save uploaded file and return the file path"""
    # Create subfolder if not exists
    folder = UPLOAD_DIR / subfolder
    folder.mkdir(exist_ok=True)
    
    # Generate unique filename
    file_ext = Path(filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {file_ext} not allowed")
    
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = folder / unique_filename
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    return str(file_path)


def process_ocr(image_path: str) -> Tuple[Optional[float], float]:
    """
    Process image with OCR to extract meter reading
    Returns: (reading_value, confidence_score)
    """
    try:
        # Open image
        image = Image.open(image_path)
        
        # Preprocess image for better OCR
        # Convert to grayscale
        image = image.convert('L')
        
        # Perform OCR
        ocr_text = pytesseract.image_to_string(image, config='--psm 6 digits')
        
        # Extract numbers from OCR text
        numbers = re.findall(r'\d+\.?\d*', ocr_text)
        
        if not numbers:
            return None, 0.0
        
        # Get the largest number (likely to be the meter reading)
        reading_value = max([float(n) for n in numbers])
        
        # Get confidence (simple heuristic based on number of digits found)
        confidence = min(len(numbers) / 5.0, 1.0)  # Normalize to 0-1
        
        return reading_value, confidence
        
    except Exception as e:
        print(f"OCR Error: {str(e)}")
        return None, 0.0


def detect_leak(device_id: str, water_usage_records: list) -> dict:
    """
    Analyze water usage patterns to detect potential leaks
    
    Parameters:
    - device_id: Device ID
    - water_usage_records: List of water usage records (sorted by timestamp)
    
    Returns:
    - Dictionary with leak detection results
    """
    if len(water_usage_records) < 24:  # Need at least 24 hours of data
        return {
            "has_leak": False,
            "leak_type": None,
            "confidence": 0.0,
            "message": "Insufficient data for leak detection"
        }
    
    # Get recent 24 hours
    recent_records = water_usage_records[-24:]
    
    # Calculate statistics
    flow_rates = [r['flow_rate'] for r in recent_records if r.get('flow_rate')]
    volumes = [r['volume'] for r in recent_records if r.get('volume')]
    
    if not flow_rates:
        return {
            "has_leak": False,
            "leak_type": None,
            "confidence": 0.0,
            "message": "No flow rate data available"
        }
    
    avg_flow = sum(flow_rates) / len(flow_rates)
    max_flow = max(flow_rates)
    min_flow = min(flow_rates)
    
    # Detection algorithms
    leak_detected = False
    leak_type = None
    confidence = 0.0
    message = "No leak detected"
    
    # 1. Continuous Flow Detection (24/7 flow)
    if min_flow > 0.5:  # Minimum flow always above 0.5 L/min
        continuous_hours = len([f for f in flow_rates if f > 0.5])
        if continuous_hours >= 20:  # 20+ hours of continuous flow
            leak_detected = True
            leak_type = "continuous_flow"
            confidence = min(continuous_hours / 24, 1.0)
            message = f"Continuous flow detected for {continuous_hours} hours. Possible leak."
    
    # 2. Abnormal Spike Detection
    if max_flow > avg_flow * 5:  # Spike is 5x average
        leak_detected = True
        leak_type = "abnormal_spike"
        confidence = 0.8
        message = f"Abnormal spike detected: {max_flow:.2f} L/min (avg: {avg_flow:.2f} L/min)"
    
    # 3. Pattern Anomaly (night usage)
    # Get usage during night hours (assuming records have timestamps)
    night_usage = []
    for record in recent_records:
        timestamp = record.get('timestamp')
        if timestamp:
            hour = timestamp.hour
            if 0 <= hour <= 5:  # Night hours: 12am - 5am
                night_usage.append(record.get('flow_rate', 0))
    
    if night_usage:
        avg_night_flow = sum(night_usage) / len(night_usage)
        if avg_night_flow > 1.0:  # Significant night usage
            leak_detected = True
            leak_type = "pattern_anomaly"
            confidence = 0.7
            message = f"Unusual night usage detected: {avg_night_flow:.2f} L/min average"
    
    # 4. Zero Flow Check (possible meter malfunction)
    zero_flow_count = len([f for f in flow_rates if f == 0])
    if zero_flow_count > 20:  # More than 20 hours of zero flow
        leak_detected = True
        leak_type = "zero_flow"
        confidence = 0.6
        message = "Extended period of zero flow detected. Possible meter malfunction."
    
    # Calculate estimated water loss if leak detected
    estimated_loss = 0.0
    if leak_detected and leak_type != "zero_flow":
        # Estimate loss in liters over 24 hours
        if leak_type == "continuous_flow":
            estimated_loss = min_flow * 60 * 24  # L/min * 60 min * 24 hours
        elif leak_type == "abnormal_spike":
            estimated_loss = (max_flow - avg_flow) * 60 * 24
        elif leak_type == "pattern_anomaly":
            estimated_loss = avg_night_flow * 60 * 5  # Night hours only
    
    return {
        "has_leak": leak_detected,
        "leak_type": leak_type,
        "confidence": confidence,
        "message": message,
        "avg_flow_rate": avg_flow,
        "max_flow_rate": max_flow,
        "min_flow_rate": min_flow,
        "estimated_loss_liters": round(estimated_loss, 2)
    }


def generate_technician_report_data(
    technician_id: str,
    start_date: datetime,
    end_date: datetime,
    readings: list,
    work_orders: list,
    issues_found: list
) -> dict:
    """Generate comprehensive technician report data"""
    
    # Calculate statistics
    total_readings = len(readings)
    total_tasks = len(work_orders)
    completed_tasks = len([w for w in work_orders if w.get('status') == 'completed'])
    
    # Get unique devices visited
    devices_visited = set()
    for reading in readings:
        devices_visited.add(reading.get('device_id'))
    for work_order in work_orders:
        if work_order.get('device_id'):
            devices_visited.add(work_order['device_id'])
    
    total_devices_visited = len(devices_visited)
    total_issues_found = len(issues_found)
    
    # Calculate performance metrics
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    avg_readings_per_day = total_readings / ((end_date - start_date).days + 1)
    
    # Generate summary
    summary = f"""
Technician Performance Report
Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}

Summary:
- Total Meter Readings: {total_readings}
- Average Readings/Day: {avg_readings_per_day:.1f}
- Total Tasks Assigned: {total_tasks}
- Tasks Completed: {completed_tasks}
- Completion Rate: {completion_rate:.1f}%
- Devices Visited: {total_devices_visited}
- Issues Found: {total_issues_found}

Performance: {'Excellent' if completion_rate > 90 else 'Good' if completion_rate > 70 else 'Needs Improvement'}
    """.strip()
    
    return {
        "total_readings": total_readings,
        "total_tasks_completed": completed_tasks,
        "total_devices_visited": total_devices_visited,
        "total_issues_found": total_issues_found,
        "summary": summary,
        "completion_rate": completion_rate,
        "avg_readings_per_day": avg_readings_per_day
    }


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calculate distance between two coordinates in kilometers
    Using Haversine formula
    """
    from math import radians, sin, cos, sqrt, atan2
    
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = radians(lat1)
    lat2_rad = radians(lat2)
    delta_lat = radians(lat2 - lat1)
    delta_lng = radians(lng2 - lng1)
    
    a = sin(delta_lat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lng/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    distance = R * c
    return distance


def optimize_route(locations: list) -> list:
    """
    Simple route optimization (nearest neighbor algorithm)
    
    Parameters:
    - locations: List of dicts with 'id', 'lat', 'lng'
    
    Returns:
    - Optimized list of location IDs
    """
    if len(locations) <= 1:
        return [loc['id'] for loc in locations]
    
    # Start from first location
    route = [locations[0]['id']]
    current = locations[0]
    remaining = locations[1:]
    
    while remaining:
        # Find nearest location
        nearest = min(
            remaining,
            key=lambda loc: calculate_distance(
                current['lat'], current['lng'],
                loc['lat'], loc['lng']
            )
        )
        
        route.append(nearest['id'])
        current = nearest
        remaining.remove(nearest)
    
    return route