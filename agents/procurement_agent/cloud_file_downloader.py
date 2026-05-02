"""
Cloud File Downloader
Downloads files from OneDrive, SharePoint, and Google Drive using OAuth2
"""
import os
import json
import base64
import requests
from pathlib import Path
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io


class CloudFileDownloader:
    """Download files from cloud storage services"""
    
    def __init__(self):
        """Initialize downloader"""
        self.onedrive_token = None
        self.google_creds = None
        self.max_file_size = 500 * 1024 * 1024  # 500 MB
    
    def download_from_onedrive(self, share_url: str, save_dir: str) -> List[str]:
        """
        Download files from OneDrive shared link
        
        Args:
            share_url: OneDrive sharing URL
            save_dir: Directory to save downloaded files
            
        Returns:
            List of downloaded file paths
        """
        print(f"[OneDrive] Downloading from: {share_url}")
        
        try:
            # Load OAuth token
            token_file = Path('.outlook_oauth_token.json')
            if not token_file.exists():
                print("[X] OneDrive OAuth token not found. Please authenticate first.")
                return []
            
            with open(token_file) as f:
                token_data = json.load(f)
                self.onedrive_token = token_data.get('access_token')
            
            if not self.onedrive_token:
                print("[X] No access token found in OAuth file")
                return []
            
            # Convert sharing URL to shareId
            share_id = self._get_share_id(share_url)
            
            # Get shared item details
            headers = {'Authorization': f'Bearer {self.onedrive_token}'}
            response = requests.get(
                f'https://graph.microsoft.com/v1.0/shares/{share_id}/driveItem',
                headers=headers
            )
            
            if response.status_code == 401:
                print("[X] OneDrive token expired. Please re-authenticate.")
                return []
            
            if response.status_code != 200:
                print(f"[X] Error accessing OneDrive link: {response.status_code}")
                print(f"    {response.text}")
                return []
            
            item = response.json()
            
            # Create save directory
            os.makedirs(save_dir, exist_ok=True)
            
            # Download files
            downloaded = []
            
            if 'folder' in item:
                # It's a folder - get children
                print(f"[OneDrive] Shared item is a folder: {item.get('name', 'Untitled')}")
                children = self._get_folder_children(share_id, headers)
                
                for child in children:
                    if 'file' in child:  # Skip subfolders for now
                        file_path = self._download_onedrive_file(child, save_dir, headers)
                        if file_path:
                            downloaded.append(file_path)
            else:
                # Single file
                print(f"[OneDrive] Shared item is a file: {item.get('name', 'Untitled')}")
                file_path = self._download_onedrive_file(item, save_dir, headers)
                if file_path:
                    downloaded.append(file_path)
            
            print(f"[OK] Downloaded {len(downloaded)} file(s) from OneDrive")
            return downloaded
        
        except Exception as e:
            print(f"[X] Error downloading from OneDrive: {e}")
            return []
    
    def download_from_google_drive(self, drive_url: str, file_id: str, save_dir: str) -> List[str]:
        """
        Download files from Google Drive
        
        Args:
            drive_url: Google Drive URL
            file_id: Extracted file/folder ID
            save_dir: Directory to save downloaded files
            
        Returns:
            List of downloaded file paths
        """
        print(f"[Google Drive] Downloading from: {drive_url}")
        
        try:
            # Load OAuth credentials
            token_file = Path('.gmail_oauth_token.json')
            if not token_file.exists():
                print("[X] Gmail OAuth token not found. Please authenticate first.")
                return []
            
            with open(token_file) as f:
                token_data = json.load(f)
            
            # Create credentials
            self.google_creds = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )
            
            # Build Drive service
            service = build('drive', 'v3', credentials=self.google_creds)
            
            # Create save directory
            os.makedirs(save_dir, exist_ok=True)
            
            # Get file metadata
            file_metadata = service.files().get(
                fileId=file_id,
                fields='id,name,mimeType,size'
            ).execute()
            
            downloaded = []
            
            # Check if it's a folder
            if file_metadata['mimeType'] == 'application/vnd.google-apps.folder':
                print(f"[Google Drive] Shared item is a folder: {file_metadata['name']}")
                
                # List files in folder
                results = service.files().list(
                    q=f"'{file_id}' in parents",
                    fields='files(id,name,mimeType,size)'
                ).execute()
                
                files = results.get('files', [])
                
                for file in files:
                    file_path = self._download_google_drive_file(service, file, save_dir)
                    if file_path:
                        downloaded.append(file_path)
            else:
                # Single file
                print(f"[Google Drive] Shared item is a file: {file_metadata['name']}")
                file_path = self._download_google_drive_file(service, file_metadata, save_dir)
                if file_path:
                    downloaded.append(file_path)
            
            print(f"[OK] Downloaded {len(downloaded)} file(s) from Google Drive")
            return downloaded
        
        except Exception as e:
            print(f"[X] Error downloading from Google Drive: {e}")
            return []
    
    def _get_share_id(self, share_url: str) -> str:
        """
        Convert OneDrive sharing URL to shareId for Graph API
        
        Args:
            share_url: OneDrive sharing URL
            
        Returns:
            Encoded shareId
        """
        # Encode URL as base64
        encoded = base64.b64encode(share_url.encode()).decode()
        
        # Remove padding and make URL-safe
        encoded = encoded.rstrip('=').replace('/', '_').replace('+', '-')
        
        # Add prefix
        return f'u!{encoded}'
    
    def _get_folder_children(self, share_id: str, headers: Dict) -> List[Dict]:
        """Get children of a OneDrive folder"""
        try:
            response = requests.get(
                f'https://graph.microsoft.com/v1.0/shares/{share_id}/driveItem/children',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('value', [])
            else:
                print(f"[!] Could not list folder contents: {response.status_code}")
                return []
        
        except Exception as e:
            print(f"[!] Error listing folder: {e}")
            return []
    
    def _download_onedrive_file(self, item: Dict, save_dir: str, headers: Dict) -> Optional[str]:
        """Download a single file from OneDrive"""
        try:
            file_name = item.get('name', 'untitled')
            file_size = item.get('size', 0)
            
            # Check file size
            if file_size > self.max_file_size:
                print(f"  [!] File too large ({file_size / 1024 / 1024:.1f} MB): {file_name}")
                return None
            
            # Get download URL
            download_url = item.get('@microsoft.graph.downloadUrl')
            
            if not download_url:
                print(f"  [!] No download URL for: {file_name}")
                return None
            
            # Download file
            print(f"  [->] Downloading: {file_name} ({file_size / 1024:.1f} KB)")
            
            response = requests.get(download_url, headers=headers)
            
            if response.status_code == 200:
                # Save file
                file_path = os.path.join(save_dir, file_name)
                
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                print(f"  [OK] Saved: {file_name}")
                return file_path
            else:
                print(f"  [X] Download failed: {response.status_code}")
                return None
        
        except Exception as e:
            print(f"  [X] Error downloading file: {e}")
            return None
    
    def _download_google_drive_file(self, service, file_metadata: Dict, save_dir: str) -> Optional[str]:
        """Download a single file from Google Drive"""
        try:
            file_id = file_metadata['id']
            file_name = file_metadata['name']
            mime_type = file_metadata['mimeType']
            file_size = int(file_metadata.get('size', 0))
            
            # Check file size
            if file_size > self.max_file_size:
                print(f"  [!] File too large ({file_size / 1024 / 1024:.1f} MB): {file_name}")
                return None
            
            print(f"  [->] Downloading: {file_name} ({file_size / 1024:.1f} KB)")
            
            # Handle Google Docs files (need export)
            if mime_type.startswith('application/vnd.google-apps.'):
                # Export Google Docs files
                export_mime = self._get_export_mime_type(mime_type)
                if not export_mime:
                    print(f"  [!] Cannot export file type: {mime_type}")
                    return None
                
                request = service.files().export_media(
                    fileId=file_id,
                    mimeType=export_mime
                )
                
                # Update filename with proper extension
                file_name = self._update_filename_for_export(file_name, export_mime)
            else:
                # Regular file download
                request = service.files().get_media(fileId=file_id)
            
            # Download to memory
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            # Save file
            file_path = os.path.join(save_dir, file_name)
            
            with open(file_path, 'wb') as f:
                f.write(fh.getvalue())
            
            print(f"  [OK] Saved: {file_name}")
            return file_path
        
        except Exception as e:
            print(f"  [X] Error downloading file: {e}")
            return None
    
    def _get_export_mime_type(self, google_mime_type: str) -> Optional[str]:
        """Get export MIME type for Google Docs files"""
        export_map = {
            'application/vnd.google-apps.document': 'application/pdf',
            'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.google-apps.presentation': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        }
        return export_map.get(google_mime_type)
    
    def _update_filename_for_export(self, filename: str, export_mime_type: str) -> str:
        """Add proper extension to exported Google Docs files"""
        extension_map = {
            'application/pdf': '.pdf',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
        }
        
        extension = extension_map.get(export_mime_type, '')
        
        # Add extension if not present
        if extension and not filename.endswith(extension):
            filename = filename + extension
        
        return filename


# Test function
if __name__ == "__main__":
    print("Testing Cloud File Downloader...")
    
    downloader = CloudFileDownloader()
    
    # Test with example URLs (replace with real URLs)
    # onedrive_url = "https://1drv.ms/f/s!..."
    # drive_url = "https://drive.google.com/file/d/..."
    
    print("\nNote: Replace URLs with real sharing links to test")
    print("Test complete!")
