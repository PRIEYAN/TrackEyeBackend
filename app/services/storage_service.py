import os
import requests
from app.config import Config
from typing import Optional
import uuid


class StorageService:
    def __init__(self):
        self.supabase_url = Config.SUPABASE_URL
        self.service_role_key = Config.SUPABASE_SERVICE_ROLE_KEY
        self.bucket = Config.STORAGE_BUCKET
    
    def upload_file(self, file_path: str, destination_path: str) -> Optional[str]:
        try:
            url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{destination_path}"
            headers = {
                "Authorization": f"Bearer {self.service_role_key}",
                "Content-Type": "application/octet-stream"
            }
            
            with open(file_path, 'rb') as f:
                response = requests.put(url, data=f, headers=headers)
            
            if response.status_code in [200, 201]:
                public_url = f"{self.supabase_url}/storage/v1/object/public/{self.bucket}/{destination_path}"
                return public_url
            else:
                return None
        except Exception as e:
            print(f"Storage upload error: {str(e)}")
            return None
    
    def delete_file(self, file_path: str) -> bool:
        try:
            url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{file_path}"
            headers = {
                "Authorization": f"Bearer {self.service_role_key}"
            }
            response = requests.delete(url, headers=headers)
            return response.status_code in [200, 204]
        except Exception:
            return False
    
    def get_signed_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        try:
            url = f"{self.supabase_url}/storage/v1/object/sign/{self.bucket}/{file_path}"
            headers = {
                "Authorization": f"Bearer {self.service_role_key}"
            }
            params = {"expires_in": expires_in}
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                signed_path = data.get('signedURL', '').split('/')[-1]
                return f"{self.supabase_url}/storage/v1{signed_path}"
            return None
        except Exception:
            return None
    
    def generate_document_path(self, shipment_id: str, filename: str) -> str:
        unique_filename = f"{uuid.uuid4()}_{filename}"
        return f"shipments/{shipment_id}/documents/{unique_filename}"

