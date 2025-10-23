import os
import uuid
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path
import json

class FileService:
    """
    Service untuk handle file uploads dengan metadata (GPS, timestamp)
    """
    
    def __init__(self):
        self.upload_dir = os.environ.get('UPLOAD_DIR', '/tmp/uploads')
        self.ticket_attachments_dir = os.path.join(self.upload_dir, 'ticket_attachments')
        self.signatures_dir = os.path.join(self.upload_dir, 'signatures')
        
        # Create directories if they don't exist
        os.makedirs(self.ticket_attachments_dir, exist_ok=True)
        os.makedirs(self.signatures_dir, exist_ok=True)
    
    def save_ticket_attachment(self, file_content: bytes, file_name: str, file_type: str, 
                               ticket_id: str, uploaded_by: str,
                               gps_coordinates: Optional[Dict] = None) -> Dict:
        """
        Save ticket attachment file with metadata
        """
        try:
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            file_extension = Path(file_name).suffix
            unique_filename = f"{ticket_id}_{file_id}{file_extension}"
            
            # Save file
            file_path = os.path.join(self.ticket_attachments_dir, unique_filename)
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Prepare metadata
            timestamp = datetime.utcnow()
            metadata = {
                'id': file_id,
                'ticket_id': ticket_id,
                'file_path': file_path,
                'file_name': file_name,
                'file_type': file_type,
                'file_size': len(file_content),
                'uploaded_by': uploaded_by,
                'uploaded_at': timestamp.isoformat(),
                'timestamp_metadata': timestamp.isoformat(),
                'gps_coordinates': gps_coordinates if gps_coordinates else None
            }
            
            # Save metadata file
            metadata_file = os.path.join(self.ticket_attachments_dir, f"{unique_filename}.metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            print(f"✅ File saved: {file_path}")
            return metadata
            
        except Exception as e:
            print(f"❌ Error saving ticket attachment: {str(e)}")
            raise
    
    def save_signature(self, signature_data: str, ticket_id: str, signed_by: str, 
                      signature_type: str, gps_coordinates: Optional[Dict] = None) -> Dict:
        """
        Save digital signature with metadata
        signature_data should be base64 encoded image
        """
        try:
            import base64
            
            # Generate unique signature ID
            signature_id = str(uuid.uuid4())
            signature_filename = f"signature_{ticket_id}_{signature_id}.png"
            
            # Decode base64 and save
            signature_path = os.path.join(self.signatures_dir, signature_filename)
            
            # Remove data URL prefix if present
            if ',' in signature_data:
                signature_data = signature_data.split(',')[1]
            
            signature_bytes = base64.b64decode(signature_data)
            with open(signature_path, 'wb') as f:
                f.write(signature_bytes)
            
            # Prepare metadata
            timestamp = datetime.utcnow()
            metadata = {
                'id': signature_id,
                'ticket_id': ticket_id,
                'signature_path': signature_path,
                'signed_by': signed_by,
                'signed_at': timestamp.isoformat(),
                'signature_type': signature_type,
                'gps_coordinates': gps_coordinates if gps_coordinates else None
            }
            
            # Save metadata file
            metadata_file = os.path.join(self.signatures_dir, f"{signature_filename}.metadata.json")
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            print(f"✅ Signature saved: {signature_path}")
            return metadata
            
        except Exception as e:
            print(f"❌ Error saving signature: {str(e)}")
            raise
    
    def get_file_metadata(self, file_id: str, file_type: str = 'attachment') -> Optional[Dict]:
        """
        Retrieve file metadata
        """
        try:
            search_dir = self.ticket_attachments_dir if file_type == 'attachment' else self.signatures_dir
            
            # Search for metadata file
            for filename in os.listdir(search_dir):
                if filename.endswith('.metadata.json') and file_id in filename:
                    metadata_path = os.path.join(search_dir, filename)
                    with open(metadata_path, 'r') as f:
                        return json.load(f)
            
            return None
            
        except Exception as e:
            print(f"❌ Error getting file metadata: {str(e)}")
            return None
    
    def delete_file(self, file_id: str, file_type: str = 'attachment') -> bool:
        """
        Delete file and its metadata
        """
        try:
            search_dir = self.ticket_attachments_dir if file_type == 'attachment' else self.signatures_dir
            
            # Find and delete both file and metadata
            deleted = False
            for filename in os.listdir(search_dir):
                if file_id in filename:
                    file_path = os.path.join(search_dir, filename)
                    os.remove(file_path)
                    deleted = True
                    print(f"✅ Deleted: {file_path}")
            
            return deleted
            
        except Exception as e:
            print(f"❌ Error deleting file: {str(e)}")
            return False
    
    def validate_gps_coordinates(self, gps_data: Dict) -> bool:
        """
        Validate GPS coordinates format
        """
        if not gps_data:
            return True  # GPS is optional
        
        required_fields = ['latitude', 'longitude']
        if not all(field in gps_data for field in required_fields):
            return False
        
        # Validate latitude (-90 to 90)
        if not (-90 <= gps_data['latitude'] <= 90):
            return False
        
        # Validate longitude (-180 to 180)
        if not (-180 <= gps_data['longitude'] <= 180):
            return False
        
        return True
    
    def format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

# Create singleton instance
file_service = FileService()
